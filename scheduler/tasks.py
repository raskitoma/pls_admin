# RSK - Core
# 2023 (c) All rights reserved
# by Raskitoma.com/Raskitoma.io
# ######################## PLEASE READ ##########################################
# This is a scheduler for the PLS Grabber
# Index of file:
# - Tasks are defined starting line 40
# - Tasks are scheduled at the last part, divided by a large comment block
#   here you can set timings, etc.
# Task are loaded in the entrypoint.py file by flask
# To run it, just use the flask command option "scheduler"
# ###############################################################################

import os
import schedule
import datetime, time
import requests
import json
from app import create_app
from app.rskcore.utl import new_log, get_time, prGreen, prYellow, prRed
from app.rskcore.str_log import *
from web3 import Web3

settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)

# setting up db
from app import db
from app.rskcore.models import pls_wallets, \
    pls_price, pls_block_explorer, \
    pls_wallet_history, pls_validator_withdrawals

# setting up configvars
REWARD_BASE_PCT = app.config['REWARD_BASE_PCT']
PLS_PRICE_URI = app.config['PLS_PRICE_URI']
PLS_PRICE_API_KEY = app.config['PLS_PRICE_API_KEY']
PLS_PRICE_FX = app.config['PLS_PRICE_FX']


# get price from provider
def get_price(uri, api_key, fx_param):
    headers = {'X-CMC_PRO_API_KEY': api_key}
    #parameters = {'convert': 'AUD'}
    parameters = {'convert': fx_param}
    try:
        response1 = requests.get(uri, headers=headers)
        response2 = requests.get(uri, headers=headers, params=parameters)
        data1 = json.loads(response1.text)
        data2 = json.loads(response2.text)
    except Exception as e:
        log2store = f"{get_time()} | Error getting data from price API: {str(e)}"
        prRed(f'{get_time()} | {log2store}')
        price_usd = pls_price.get_last().priceUSD
        price_fx = pls_price.get_last().priceFX
        return price_usd, price_fx
    try:
        price_usd = float(data1['data']['11145']['quote']['USD']['price'])
        price_fx = float(data2['data']['11145']['quote'][fx_param]['price'])
    except Exception as e:
        log2store = f"{get_time()} | Error getting price from API: {str(e)}"
        prRed(f'{get_time()} | {log2store}')
        price_usd = pls_price.get_last().priceUSD
        price_fx = pls_price.get_last().priceFX
    return price_usd, price_fx

# ###############################################################################
# setting up tasks
# ###############################################################################

# Gets PLS Price from source
def pls_price_update():
    everything_ok = True
    log2store = 'Update PLS Price - Start'
    prYellow(f'{get_time()} | SCHEDULER ====================>>> {log2store}')
    new_log(users_id=1, module='PRICE_UPDATE', severity=SEV_INF, description=log2store, data=log2store, image=None)
    # get PLS price
    try:
        price_usd, price_fx = get_price(PLS_PRICE_URI, PLS_PRICE_API_KEY, PLS_PRICE_FX)
    except Exception as e:
        log2store = f"{get_time()} | Error getting data from price API: {str(e)}"
        prRed(f'{get_time()} | {log2store}')
        new_log(users_id=1, module='PRICE_UPDATE', severity=SEV_ERR, description=log2store, data=log2store, image=None)
        everything_ok = False
    if everything_ok:
        # store price in db
        try:
            pls_price.store_new_price(price_usd, price_fx)
        except Exception as e:
            log2store = f"{get_time()} | Error storing price in db: {str(e)}"
            prRed(f'{get_time()} | SCHEDULER ==> {log2store}')
            new_log(users_id=1, module='PRICE_UPDATE', severity=SEV_ERR, description=log2store, data=log2store, image=None)
    log2store = 'Update PLS Price - End'
    print(f'{get_time()} | {log2store}')
    new_log(users_id=1, module='PRICE_UPDATE', severity=SEV_INF, description=log2store, data=log2store, image=None)

# Updates Wallets data
def wallets_review():
    log2store = 'Wallets Update - Start'
    prYellow(f'{get_time()} | SCHEDULER ====================>>> {log2store}')
    new_log(users_id=1, module='PLS_WALLET', severity=SEV_INF, description=log2store, data=log2store, image=None)
    # get all wallets
    pls_wallets_list = pls_wallets.query.all()
    price_usd, price_fx = get_price(PLS_PRICE_URI, PLS_PRICE_API_KEY, PLS_PRICE_FX)
    for wallet in pls_wallets_list:
        wallet_data_uri = f'https://scan.pulsechain.com/api?module=account&action=balance&address={wallet.address}'
        wallet_data = requests.get(wallet_data_uri)
        if wallet_data.status_code == 200:
            wallet_info = wallet_data.json()
            if wallet_info['status'] == '1':
                # save new value for history purposes
                current_balance = wallet_info['result']
                previous_balance = pls_wallets.get_balance(wallet.address)
                #balance_diff = float(current_balance) - previous_balance
                #prGreen(f'{current_balance}')
                #prGreen(f'{previous_balance}')
                #print(f'{balance_diff}')
                if float(current_balance) != previous_balance:
                    if float(current_balance) > previous_balance:
                        balance_increase = float(current_balance) - previous_balance
                        if balance_increase < 32000000:
                            #increase in balance from validator rewards and/or fee recipient tips/rewards
                            taxableIncome_USD = balance_increase * price_usd
                            taxableIncome_FX = balance_increase * price_fx
                        else:
                            #increase in balance caused by exiting validator/s with or without validator
                            #rewards and/or fee recipient tips/rewards
                            taxableIncome_USD = (balance_increase - (balance_increase//32000000 * 32000000)) * price_usd
                            taxableIncome_FX = (balance_increase - (balance_increase//32000000 * 32000000)) * price_fx
                    else:
                        taxableIncome_USD = 0
                        taxableIncome_FX = 0
                    pls_wallet_history.new_balance(wallet.address, current_balance, price_usd, price_fx, taxableIncome_USD, taxableIncome_FX)
                    # update wallet balance
                    pls_wallets.update_balance(wallet.address, current_balance)
                    log2store = f'Wallet {wallet.address} updated with balance {current_balance}'
                    prGreen(f'{get_time()} | {log2store}')
                else:
                    log2store = f'Wallet {wallet.address} not updated, balance is the same'
                    prYellow(f'{get_time()} | {log2store}')
            else:
                log2store = f'Wallet {wallet.address} not found'
                prRed(f'{get_time()} | {log2store}')
        else:
            log2store = f'Wallet {wallet.address} not found'
            prRed(f'{get_time()} | {log2store}')
    log2store = 'Wallets Update - End'
    print(f'{get_time()} | {log2store}')
    new_log(users_id=1, module='PLS_WALLET', severity=SEV_INF, description=log2store, data=log2store, image=None)                     


# Search for new mined blocks and validators
def validator_update():
    # fire up web3
    web3 = Web3(Web3.HTTPProvider(app.config['WEB3_PROVIDER_URI']))
    block_current = web3.eth.get_block_number()
    block_last_managed = pls_block_explorer.get_last()
    block_last_height = app.config['MAX_HEIGHT_CHECK'] if block_last_managed is None else block_last_managed.blockheight
    # get pls current price, we don't need too much precision, it's good enough to get this price on this run for all withdrawals found
    # and also is good to no stress and overload the API
    price_usd, price_fx = get_price(PLS_PRICE_URI, PLS_PRICE_API_KEY, PLS_PRICE_FX)
    # get wallets
    wallets = pls_wallets.get_all()
    for wallet in wallets:
        trx_count = web3.eth.get_transaction_count(wallet.address, block_current)
        log2store = f'Wallet {wallet.address} has {trx_count} transactions - Checking from block {block_current} to {block_last_height}'
        prYellow(f'{get_time()} | {log2store}')
        wallet_processed_qty = 0
        for i in range(block_current, block_last_height, -1):
            log2store = f'Checking block {i}'
            print(f'\r{get_time()} | {log2store}', end='')
            block_data = web3.eth.get_block(i)
            if block_data.withdrawals:
                for withdrawal in block_data.withdrawals:
                    if withdrawal['address'] == wallet.address:
                        log2store = f'Withdrawal found: {withdrawal["index"]}'
                        prGreen(f'\n{get_time()} | {log2store}')
                        w_index = int(withdrawal['index'])
                        # lets check if this withdrawal is already in the db
                        if pls_validator_withdrawals.get_one_by_index(w_index) is None:
                            w_validatorIndex = int(withdrawal['validatorIndex'])
                            w_blockNumber = i
                            w_amount = float(withdrawal['amount'])
                            w_miner = block_data.miner
                            w_timestamp = datetime.datetime.fromtimestamp(int(block_data.timestamp))
                            w_address = wallet.address
                            w_price_usd = price_usd
                            w_price_fx = price_fx
                            new_withdrawal_data = pls_validator_withdrawals(
                                index = w_index,
                                validatorIndex = w_validatorIndex,
                                blockNumber = w_blockNumber,
                                amount = w_amount,
                                miner = w_miner,
                                timeStamp = w_timestamp,
                                address = w_address,
                                priceUSD = w_price_usd,
                                priceFX = w_price_fx
                            )
                            db.session.add(new_withdrawal_data)
                            try:
                                db.session.commit()
                                log2store = f'Withdrawal found: {w_index} | {w_validatorIndex} | Stored into DB!'
                                prGreen(f'{get_time()} | {log2store}')
                                wallet_processed_qty += 1
                            except Exception as e:
                                log2store = f"{get_time()} | Error storing withdrawal in db: {str(e)}"
                                prRed(f'{get_time()} | SCHEDULER ==> {log2store}')                        
    # once all are reviewed, update last block managed
    try:
        blockupdate = pls_block_explorer(
            blockheight=block_current,
            date=datetime.datetime.now()
        )
        db.session.add(blockupdate)
        db.session.commit()
        log2store = f'Last block managed: {block_current}, updated {wallet_processed_qty} withdrawals'
        print(f'{get_time()} | {log2store}')
    except Exception as e:
        log2store = f"{get_time()} | Error updating last block managed: {str(e)}"
        prRed(f'{get_time()} | SCHEDULER ==> {log2store}')


# Search for new mined blocks and validators
def pls_custom_sync(xfrom, xto):
    # fire up web3
    web3 = Web3(Web3.HTTPProvider(app.config['WEB3_PROVIDER_URI']))
    # get pls current price, we don't need too much precision, it's good enough to get this price on this run for all withdrawals found
    # and also is good to no stress and overload the API
    price_usd, price_fx = get_price(PLS_PRICE_URI, PLS_PRICE_API_KEY, PLS_PRICE_FX)
    # get wallets    
    wallets = pls_wallets.get_all()    
    for wallet in wallets:
        log2store = f'Wallet {wallet.address} - Checking from block {xfrom} to {xto}'
        prYellow(f'{get_time()} | {log2store}')
        wallet_processed_qty = 0
        for i in range(xfrom, xto, -1):
            log2store = f'Checking block {i}'
            print(f'\r{get_time()} | {log2store}', end='')
            block_data = web3.eth.get_block(i)
            if block_data.withdrawals:
                for withdrawal in block_data.withdrawals:
                    if withdrawal['address'] == wallet.address:
                        log2store = f'Withdrawal found: {withdrawal["index"]}'
                        prGreen(f'\n{get_time()} | {log2store}')
                        w_index = int(withdrawal['index'])
                        w_validatorIndex = int(withdrawal['validatorIndex'])
                        w_blockNumber = i
                        w_amount = float(withdrawal['amount'])
                        w_miner = block_data.miner
                        w_timestamp = datetime.datetime.fromtimestamp(int(block_data.timestamp))
                        w_address = wallet.address
                        w_price_usd = price_usd
                        w_price_fx = price_fx
                        new_withdrawal_data = pls_validator_withdrawals(
                            index = w_index,
                            validatorIndex = w_validatorIndex,
                            blockNumber = w_blockNumber,
                            amount = w_amount,
                            miner = w_miner,
                            timeStamp = w_timestamp,
                            address = w_address,
                            priceUSD = w_price_usd,
                            priceFX = w_price_fx
                        )
                        db.session.add(new_withdrawal_data)
                        try:
                            db.session.commit()
                            log2store = f'Withdrawal found: {w_index} | {w_validatorIndex} | Stored into DB!'
                            prGreen(f'{get_time()} | {log2store}')
                            wallet_processed_qty += 1
                        except Exception as e:
                            log2store = f"{get_time()} | Error storing withdrawal in db: {str(e)}"
                            prRed(f'{get_time()} | SCHEDULER ==> {log2store}')                        

                                    
# ###############################################################################
# ###############################################################################
# setting up scheduler
# ###############################################################################
# ###############################################################################

schedule.every(10).minutes.do(pls_price_update)
schedule.every(6).minutes.do(wallets_review)
schedule.every().hour.at(":15").do(validator_update)
schedule.every().hour.at(":45").do(validator_update)
