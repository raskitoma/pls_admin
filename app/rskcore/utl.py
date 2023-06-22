#############################################
# core_utl.py
# (c)2023, Raskitoma.com
#--------------------------------------------
# Multiple utility functions for Core
#-------------------------------------------- 
# TODO - Add extra functionality
#-------------------------------------------- 
# Getting libraries
import base64
import os
from re import template
import stat
import random
import json
import time
from markupsafe import Markup
import requests
import jwt
import uuid
import string
from datetime import timedelta, datetime
from dateutil import relativedelta
from flask import jsonify, render_template, make_response, session, request, current_app
from werkzeug.security import check_password_hash
from functools import wraps
from sqlalchemy import false
from app import db, mail, logging, HEADER_01_KEY, HEADER_01_VAL
from .str import *
from .str_log import *
from flask_mailman import EmailMessage
from .models import Users
from .models import logs
from .models import master_config

logger = logging.getLogger(__name__)

# Some constants
MSG_MIS_TOKEN = 'Token is missing!'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

# Some utility functions
def make_full_name(first_name, middle_name=None, last_name=None):
    '''
    Creates a full name from the first, middle and last name parameters.
        Parameters:
            first_name (string): First name
            middle_name (string): Middle name
            last_name (string): Last name
        Returns:
            String
    '''
    middle_name = f' {middle_name} ' if middle_name else ''
    last_name = f' {last_name}' if last_name else ''
    return f'{first_name}{middle_name}{last_name}'

def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
 
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
 
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
 
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
 
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
 
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
 
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))

def get_time():
    return time.strftime("%d/%m/%Y %H:%M:%S")

def monthdiff(start_date, end_date):
    '''
    Calculates the difference in months between two dates
        Parameters:
            date1 (datetime): First date
            date2 (datetime): Second date
        Returns:
            Integer
    '''
    rdelta = relativedelta.relativedelta(end_date, start_date)
    months_diff = rdelta.years * 12 + rdelta.months
    return months_diff

def handle_folder_error(func, path, exc_info):
    '''
    Handles error when trying to delete folders. Changes the actual attributes of the folder and
    its contents to allow the process to continue.
        Parameters:
            func (object): Function object
            path (string): Path for file
            exc_info (string): 
        Returns:
            Object
    '''
    logger.info('Handling Error for file: ' + path)
    logger.info(exc_info)
    # Check if file access issue
    if not os.access(path, os.W_OK):
       logger.info('Trying to change permission to delete the project')
       # Try to change the permision of file
       os.chmod(path, stat.S_IWUSR)
       # call the calling function again
       func(path)

def rand_string(length=6, my_haystack='ABCDEF0123456789'):
    '''
    Returns a scrambled random string with a defined length, based on a haystack of characters.
        Parameters:
            length (int): A decimal integer, default=6.
            my_haystack(string): A string source used for the random string generation, default=ABCDEF0123456789.\
        Returns:
            String
    '''
    return ''.join((random.choice(my_haystack) for _ in range(length)))

def err_json(daerror):
    '''
    Standarizes any error string and format it into a standard JSON object
        Parameters:
            daerror (string): String to be formatted
        Returns:
            Serialized object
    '''
    error_dict = {}
    error_dict.update({'error': str(daerror)})
    return json.dumps(error_dict)

def str_to_bool(s):
    '''
    Converts a string to a boolean value.
        Parameters:
            s (string): String to be converted
        Returns:
            Boolean or error msg
    '''
    try:
        if s.upper() == 'TRUE':
            return True
        elif s.upper() == 'FALSE':
            return False
        else:
            return '{}: is not boolean!'.format(s)
    except Exception as e:
        return 'Error {}'.format(e)  

def parse_cron_string(cron_string):
    cron_fields = ['minute', 'hour', 'day_of_month', 'month', 'day_of_week']
    cron_values = cron_string.split()
    if len(cron_values) != len(cron_fields):
        raise ValueError('Invalid cron string')
    cron_dict = dict(zip(cron_fields, cron_values))
    return cron_dict

def new_log(users_id, module, severity, description, data, image):
    '''
    Grabs the data and stores it into the logs table
        Parameters:
            users_id (int): User ID
            module (string): Module name
            severity (string): Severity level
            description (string): Description
            data (string): Data
            image (string): Image
        Returns:
            Serialized object
    '''
    try:
        log_obj = logs(timestamp=datetime.now(), users_id=users_id, module=module, severity=severity, description=description, data=data, image=image)
        db.session.add(log_obj)
        db.session.commit()
        logger.info('Log stored')
    except Exception as e:
        logger.error('Critical error: {}'.format(e))
        return err_json('Critical error: {}'.format(e))
    
def decode_img(stringo):
    '''
    Breaks a string into bites of a defined size
        Parameters:
            stringo (string): String to be broken
            Returns: List
        Returns:
            base64 decoded string
    '''
    s = stringo.encode('utf-8')
    return base64.b64decode(s)

def encode_img(the_image):
    '''
    Encodes an image into a string
        Parameters:
            imagefile (string): Path to image file
        Returns:
            base 64 encoded string
    '''
    return [base64.b64encode(the_image).decode('utf-8')]

def generate_api_response(response_obj, response_status_code):
    '''
    Generates a response object for API calls
        Parameters:
            response_obj (object): Response object
            response_status_code (int): Response status code
        Returns:
            Serialized object
    '''
    resp = make_response(response_obj, response_status_code)
    resp.headers[HEADER_01_KEY] = HEADER_01_VAL
    return resp

def get_data_from_response(response):
    '''
    Gets the object from the response
    Parameters:
        response: The response object
    Returns:
        Object: The object from the response
    '''
    try:
        return json.loads(bytes.decode(response.response[0]))
    except Exception as e:
        logger.error('Critical error getting data object: {}'.format(str(e)))
        return None

def list_to_dict(list_object):
    '''
    Converts a list to a dict
    Parameters:
        list_object: The list object
    Returns:
        Dict: The dict object
    '''
    it = iter(list_object)
    zipped = zip(it, it) 
    response = dict(zipped)
    return response
   
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            data = request.headers['Authorization']
            try:
                token = data.split(' ')[1]
            except Exception as e:
                logger.error('Error getting token: {}'.format(str(e)))
                return generate_api_response({ 'message' : MSG_MIS_TOKEN }, 401)
        if not token:
            session['logged_in'] = false
            session.clear()
            logger.error('Token not found')
            return generate_api_response({'message': MSG_MIS_TOKEN}, 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
            token = request.args.get('token')
        except Exception as e:
            logger.error('Token is invalid! - Error: {}'.format(str(e)))
            return generate_api_response({'message': 'Token is invalid! - Error: {}'.format(e)}, 401)
        logger.info('Token valid, authenticated')
        return f(current_user, *args, **kwargs)
    return decorator

def user_login(login_details):
    '''
    Logs in a user
    Parameters:
        login_details: The login details
    Returns:
        Dict: The dict object with the response: status, message, token
    
    '''
    if (login_details is None) or (login_details.get('username') is None) or (login_details.get('password') is None):
        log2store = LOG_LOGIN_MISSING % (None, login_details)
        logger.error(log2store)
        new_log(users_id=None, module='Login', severity=SEV_ERR, description=f'{__name__} | Login: Missing Login details', data=log2store, image=None)
        return generate_api_response( { 'message' : 'Missing login details' }, 411)
    username = login_details['username']
    password = login_details['password']
    try:        
        user = Users.get_by_email(username)
    except Exception as e:
        log2store = LOG_LOGIN_ERROR % (username, str(e))
        logger.critical(log2store)
        new_log(users_id=None, module='Login', severity=SEV_CRT, description=f'{__name__} | Login: Error', data=log2store, image=None)
        return generate_api_response( {'message': 'Error: {}'.format(e)}, 500 )
    if user is None:
        log2store = LOG_LOGIN_NOTFOUND % (username)
        logger.warn(log2store)
        new_log(users_id=None, module='Login', severity=SEV_WRN, description=f'{__name__} | Login: Not found', data=log2store, image=None)
        return generate_api_response( {'message': 'Login details incorrect!'}, 404 )
    if check_password_hash(user.password, password):
        if not user.is_active:
            log2store = LOG_LOGIN_DISABLED % (username)
            logger.warn(log2store)
            new_log(users_id=user.id, module='Login', severity=SEV_WRN, description=f'{__name__} | Login: Disabled', data=log2store, image=None)
            return generate_api_response( {'message': 'Login disabled, contact admin.'}, 403 )
        session['logged_in'] = True
        session['suid'] = user.id
        payload = {
                'exp': datetime.utcnow() + timedelta(days=0, minutes=current_app.config['SESSION_TIMEOUT']),
                'iat': datetime.utcnow(),
                'sub': user.email
            }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        log2store = LOG_LOGIN_SUCCESS % (username)
        logger.info(log2store)
        new_log(users_id=user.id, module='Login', severity=SEV_INF, description=f'{__name__} | Login: Success', data=log2store, image=None)
        return generate_api_response( {'token': token, 'message' : 'Login successful!' }, 200 )
    else:
        log2store = LOG_LOGIN_PASSWORD % (username, login_details)
        logger.warn(log2store)
        new_log(users_id=None, module='Login', severity=SEV_WRN, description=f'{__name__} | Login: Password Error', data=log2store, image=None)
        return generate_api_response( {'message': 'Login details incorrect!'}, 401 )

def logout(my_user):
    log2store = LOG_LOGIN_LOGOUT % (my_user)
    logger.info(log2store)
    new_log(users_id=None, module='Login', severity=SEV_INF, description=f'{__name__} | Login: Logout', data=log2store, image=None)
    # destroy session
    session['logged_in'] = False
    session.clear()
    return generate_api_response({'message': 'Logout success!'}, 200)

def generate_uuid():
    return str(uuid.uuid4())

def get_var_value(var_name=None, db_object=master_config):
    '''
    Gets the value of a variable from the db. If not found, gets it from the config file or None.
    Params:
      - var_name: The name of the variable to get
      - app_config: The config var (flask app) to get the value from
      - db_object: The db object to get the value from
    '''
    # try to locate value from db
    var_data = db_object.get_one_by_name(var_name)
    if var_data is not None:
        configvalue = var_data.configvalue
        configtype = var_data.configtype
        if configtype == 'string':
            return str(configvalue)
        elif configtype == 'int':
            return int(configvalue)
        elif configtype == 'float':
            return float(configvalue)
        elif configtype == 'bool':
            return bool(configvalue)
        elif configtype == 'list':
            return list(configvalue)
        elif configtype == 'dict':
            return dict(configvalue)
        elif configtype == 'json':
            return json.loads(configvalue)
        else:
            return None        
    elif current_app.config.get(var_name) is not None:
        return current_app.config.get(var_name)
    else:
        return None    

def format_currency_html_markup(currency_value=0, currency_symbol='$', currency_spaces=12 , currency_decimals=2):
    '''
    Receives a float value and converts it into the specified currency format.
    Params:
      - currency_value: The value to format
      - currency_symbol: The currency symbol to use
      - currency_spaces: The number of spaces to add before the currency symbol
      - currency_decimals: The number of decimals to show
    Returns:
        - str: The formatted currency
    '''
    # format the currency
    currency_format = '{:>' + str(currency_spaces + len(currency_symbol)) + ',.' + str(currency_decimals) + 'f}'
    currency_result = currency_format.format(currency_value)
    currency_result = f'{currency_symbol}{currency_result}'
    return currency_result
    

def mail_send(mailer, mail_subject, mail_from, mail_to, mail_body):
    print(type(mailer))
    # send mail
    if mail is not None:
        mail_data_log = {
            mail_subject: mail_subject,
            mail_from: mail_from,
            mail_to: mail_to,
            mail_body: mail_body
        }
        msg =EmailMessage(
            subject=mail_subject,
            from_email=mail_from,
            to=[mail_to]
        )
        msg.body = mail_body
        msg.content_subtype = "html"
        try:
            msg.send()
            logger.info('Mail sent!')
            return generate_api_response({'message': 'Mail sent!'}, 200)
        except Exception as e:
            logger.error('Mail error: {}'.format(str(e)))
            return generate_api_response( { 'message' : 'Mail Error! - {}'.format(str(e)) }, 500)
    else:
        logger.error('Mail not configured')
        return generate_api_response( { 'message' : 'Mail not configured' }, 403)

def temp_file_maker(req_file, folder):
    uploaded_file = req_file
    filename = str(uuid.uuid4())+ '.' + uploaded_file.filename.split('.')[-1]
    try:
        uploaded_file.save(os.path.join(folder, filename))
    except Exception as e:
        logger.error(str(e))
        return False
    return filename

def temp_file_maker_no_ext(folder, my_ext):
    return os.path.join(folder, str(uuid.uuid4()) + '.' + my_ext)
    
def temp_file_killer(filename):
    try:
        os.remove(filename)
    except Exception as e:
        logger.error(str(e))
        return False
    return True

#############################################
# EoF