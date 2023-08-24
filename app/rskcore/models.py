#############################################
# Models
# (c)2023, Raskitoma.com
#--------------------------------------------
# Master DB Models
#-------------------------------------------- 
from app import db, dump_datetime
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
      
class logs(db.Model):
    '''
    logs table
    '''
    __tablename__ = 'logs'
    id = db.Column('id', db.Integer, primary_key = True) # Log id
    timestamp = db.Column('timestamp', db.DateTime, nullable = False) # Log time stamp
    users_id = db.Column('users_id', db.Integer, db.ForeignKey("users.id"), nullable = True) # User id related to log
    module = db.Column('module', db.String(30), nullable = False) # Log reporting module
    severity = db.Column('type', db.String(30), nullable = False) # Log entry type
    description = db.Column('description', db.Text, nullable = False) # Log description
    data = db.Column('data', db.Text) # Log related data (html etc)
    image = db.Column('image', db.Text, nullable = True) # Log related binary data (screenshot)
    users_rel = db.relationship('Users', backref=db.backref('users_logs', lazy=True))

    def __init__(self, timestamp, users_id, module, severity, description, data, image):
        self.timestamp = timestamp
        self.users_id = users_id
        self.module = module
        self.severity = severity
        self.description = description
        self.data = data
        self.image = image

    def __repr__(self):
        return f'TS={dump_datetime(self.timestamp)}, DESC={self.description}, USER={self.users_id}'

    @staticmethod
    def all_paginated(page=1, per_page=20):
        return logs.query.order_by(logs.timestamp.desc()).paginate(page, per_page, False)

    @property
    def serialize(self):
        '''
        Just to return object data in an easy, serializable way
        '''
        return {
            'id'         : self.id,
            'timestamp'  : dump_datetime(self.timestamp),
            'users_id'   : self.users_id,
            'module'     : self.module,
            'severity'   : self.severity,
            'description': self.description,
            'data'       : self.data,
            'image'      : self.image
        }
        
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_id(self):
        return self.id
        
    @staticmethod
    def get_all():
        return logs.query.all()
    
    @staticmethod
    def get_one(id):
        return logs.query.filter_by(id=id).first()
    
    @staticmethod
    def get_severity(severity):
        return logs.query.filter_by(severity=severity).all()
    
    @staticmethod
    def get_module(module):
        return logs.query.filter_by(module=module).all()
    
    @staticmethod
    def get_user(user):
        return logs.query.filter_by(users_id=user).all()     

class Users(db.Model, UserMixin):
    '''
    users table
    '''
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key = True) # User id
    created_at = db.Column('created_at', db.DateTime, nullable = False) # User creation time
    modified_at = db.Column('modified_at', db.DateTime, nullable = False) # User creation time
    email = db.Column('email', db.String(100), nullable = False, unique = True) #User email
    fullname = db.Column('fullname', db.String(100), nullable = True) # User fullname
    password = db.Column('password', db.Text, nullable = True) # User password
    active = db.Column('active',db.Boolean, nullable = False, default=True) # User active
    verified = db.Column('verified', db.DateTime, nullable = True, default=None) # User verified date
    access = db.Column('access', JSON, nullable = True, default=None) # User access areas
    admin = db.Column('admin', db.Boolean, nullable = False, default = False) # User admin status
    staff = db.Column('staff', db.Boolean, nullable = False, default = False) # User staff status

    def __init__(self, created_at, modified_at, email, fullname, password, active, verified, access, admin, staff):
        self.email = email
        self.fullname = fullname
        self.password = password
        self.active = active
        self.created_at = created_at
        self.modified_at = modified_at
        self.verified = verified
        self.access = access
        self.admin = admin
        self.staff = staff

    def __repr__(self):
        return f'<User {self.email}> {self.fullname}'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_id(self):
        return self.id
    
    def __unicode__(self):
        return self.fullname       

    @property
    def serialize(self):
        return {
            'id'         : self.id,
            'email'      : self.email,
            'fullname'   : self.fullname,
            'password'   : self.password,
            'status'     : self.status,
            'created_at' : dump_datetime(self.created_at),
            'verified_at': dump_datetime(self.verified_at),
            'admin'      : self.admin,
            'staff'      : self.staff
        }
                  
    @property
    def is_admin(self):
        return self.admin

    @property
    def is_staff(self):
        return self.staff
    
    @property
    def is_verified(self):
        return self.verified is not None
    
    @property
    def verified_status(self):
        return self.verified is not None
    
    @property
    def is_enabled(self):
        return self.active

    @staticmethod
    def get_by_id(id):
        return Users.query.get(id)

    @staticmethod
    def get_by_email(email):
        return Users.query.filter_by(email=email).first()

    @staticmethod
    def get_all():
        return Users.query.all()
    
    @staticmethod
    def get_staff():
        return Users.query.filter_by(staff=True).all()
    
    @staticmethod
    def get_admins():
        return Users.query.filter_by(admin=True).all()
    

class sysalerts(db.Model):
    '''
    System alerts table
    '''
    __tablename__ = 'sysalerts'
    id = db.Column('id', db.Integer, primary_key = True) # Alert id
    created_at = db.Column('created_at', db.DateTime, nullable = False) # Alert creation time
    modified_at = db.Column('modified_at', db.DateTime, nullable = False) # Alert creation time
    alert_owner = db.Column('alert_owner', db.Integer, db.ForeignKey('users.id'), nullable = False) # Alert owner (user id
    alert = db.Column('alert', db.String(200), nullable = False) # Alert text
    alert_type = db.Column('alert_type', db.String(50), nullable = False) # Alert type
    alert_status = db.Column('alert_status', db.String(50), nullable = False) # Alert status
    alert_url = db.Column('alert_url', db.String(200), nullable = True) # Alert url
    alert_url_text = db.Column('alert_url_text', db.String(50), nullable = True) # Alert url text
    alert_icon = db.Column('alert_icon', db.String(50), nullable = True) # Alert icon
    alert_color = db.Column('alert_color', db.String(50), nullable = True) # Alert color
    alert_dismissed = db.Column('alert_dismissed', db.Boolean, nullable = False, default = False) # Alert dismissed
    alert_dismissed_at = db.Column('alert_dismissed_at', db.DateTime, nullable = True, default = None) # Alert dismissed at
    alert_dismissed_by = db.Column('alert_dismissed_by', db.Integer, db.ForeignKey("users.id"), nullable = True, default = None) # Alert dismissed by
    alert_dismissed_obs = db.Column('alert_dismissed_obs', db.Text, nullable = True, default = None) # Alert dismissed observation
    alert_owner_rel = db.relationship('Users', foreign_keys=[alert_owner])
    alert_dismissed_by_rel = db.relationship('Users', foreign_keys=[alert_dismissed_by])

    def __init__(self, created_at, modified_at, alert_owner, alert, alert_type, alert_status, alert_url, alert_url_text, alert_icon, alert_color, alert_dismissed, alert_dismissed_at, alert_dismissed_by, alert_dismissed_obs):
        self.created_at = created_at
        self.modified_at = modified_at
        self.alert_owner = alert_owner
        self.alert = alert
        self.alert_type = alert_type
        self.alert_status = alert_status
        self.alert_url = alert_url
        self.alert_url_text = alert_url_text
        self.alert_icon = alert_icon
        self.alert_color = alert_color
        self.alert_dismissed = alert_dismissed
        self.alert_dismissed_at = alert_dismissed_at
        self.alert_dismissed_by = alert_dismissed_by
        self.alert_dismissed_obs = alert_dismissed_obs

    def __repr__(self):
        return f'<Alert {self.id}> {self.alert}'

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_id(self):
        return self.id

    @property
    def serialize(self):
        return {
            'created_at'        : dump_datetime(self.created_at),
            'modified_at'       : dump_datetime(self.modified_at),
            'alert_owner'       : self.alert_owner,
            'alert'             : self.alert,
            'alert_type'        : self.alert_type,
            'alert_status'      : self.alert_status,
            'alert_url'         : self.alert_url,
            'alert_url_text'    : self.alert_url_text,
            'alert_icon'        : self.alert_icon,
            'alert_color'       : self.alert_color,
            'alert_dismissed'   : self.alert_dismissed,
            'alert_dismissed_at': dump_datetime(self.alert_dismissed_at),
            'alert_dismissed_by': self.alert_dismissed_by,
            'alert_dismissed_obs': self.alert_dismissed_obs,
        }

    @staticmethod
    def get_all():
        return sysalerts.query.all()
    
    @staticmethod
    def get_last_n(n):
        return sysalerts.query.order_by(sysalerts.id.desc()).limit(n).all()

    @staticmethod
    def get_all_by_user(user_id):
        return sysalerts.query.filter_by(alert_owner=user_id).all()

    @staticmethod
    def get_last_n_by_user(user_id, n):
        return sysalerts.query.filter_by(alert_owner=user_id).order_by(sysalerts.id.desc()).limit(n).all()

    @staticmethod
    def get_last_n_active_by_user(user_id, n):
        return sysalerts.query.filter_by(alert_owner=user_id, alert_dismissed=False).order_by(sysalerts.id.desc()).limit(n).all()

    @staticmethod
    def get_all_filtered(user_id, alert_dismissed=None, alert_type=None, alert_status=None, from_date=None, upto_date=None, n=None, order_by='desc'):
        query = sysalerts.query.filter_by(alert_owner=user_id, alert_dismissed=alert_dismissed, alert_type=alert_type, alert_status=alert_status)
        if from_date is not None:
            query = query.filter(sysalerts.created_at >= from_date)
        if upto_date is not None:
            query = query.filter(sysalerts.created_at <= upto_date)
        if order_by == 'desc':
            query = query.order_by(sysalerts.id.desc())
        elif order_by == 'asc':
            query = query.order_by(sysalerts.id.asc())
        if n is not None:
            query = query.limit(n)
        return query.all()


class master_config(db.Model):
    '''
    var Config table
    '''
    __tablename__ = 'master_config'
    id = db.Column('id', db.Integer, primary_key = True)
    configname = db.Column('configname', db.String(100), nullable = False, unique=True)
    configtype = db.Column('configtype', db.Enum('string', 'int', 'float', 'bool', 'list', 'dict', 'json', name='configtype'), nullable = False)
    configvalue = db.Column('configvalue', db.Text, nullable = False)
    configstatus = db.Column('configstatus', db.Boolean, nullable = False, default = True)
    
    def __init__(self, configname, configtype, configvalue, configstatus):
        self.configname = configname
        self.configtype = configtype
        self.configvalue = configvalue
        self.configstatus = configstatus
        
    def __repr__(self):
        return f'{self.configname} - {self.configtype} - {self.configvalue} - {self.configstatus}'
    
    @staticmethod
    def get_all():
        return master_config.query.all()
    
    @staticmethod
    def get_one_by_name(configname):
        return master_config.query.filter_by(configname=configname).first()
    
    @staticmethod
    def get_all_active():
        return master_config.query.filter_by(configstatus=True).all()
    
    
class pls_wallets(db.Model):
    '''
    wallets Table
    '''
    __tablename__ = 'pls_wallets'
    address = db.Column('address', db.String(100), primary_key = True)
    owner = db.Column('owner', db.String(100), nullable = False)
    balance = db.Column('balance', db.Float, default=0, nullable = True)
    units = db.Column('units', db.String(10), default='PLS', nullable = True)
    
    def __init__(self, address, owner, balance, units):
        self.address = address
        self.owner = owner
        self.balance = balance
        self.units = units
    
    def __repr__(self):
        return f'{self.address} - {self.owner} - {self.balance} - {self.units}'
    
    @staticmethod
    def get_all():
        return pls_wallets.query.all()
    
    @staticmethod
    def get_one_by_address(address):
        return pls_wallets.query.filter_by(address=address).first()
    
    @staticmethod
    def update_balance(address, balance):
        wallet = pls_wallets.query.filter_by(address=address).first()
        wallet.balance = balance
        db.session.commit()
        return wallet
    
    @staticmethod
    def get_balance(address):
        wallet = pls_wallets.query.filter_by(address=address).first()
        return wallet.balance
    
class pls_wallet_history(db.Model):
    '''
    Wallet history
    '''
    __tablename__ = 'pls_wallet_history'
    id = db.Column('id', db.Integer, primary_key = True)
    address = db.Column('address', db.String(100), db.ForeignKey('pls_wallets.address'), nullable = False)
    balance = db.Column('balance', db.Float, nullable = False)
    date = db.Column('date', db.DateTime, nullable = False)
    priceUSD = db.Column('priceUSD', db.Float, nullable = True)
    priceFX = db.Column('priceFX', db.Float, nullable = True)
    taxableIncomeUSD = db.Column('taxableIncomeUSD', db.Float, nullable = True)
    taxableIncomeFX = db.Column('taxableIncomeFX', db.Float, nullable = True)
    
    def __init__(self, address, balance, date, price_usd, price_fx, taxableIncome_usd, taxableIncome_fx):
        self.address = address
        self.balance = balance
        self.date = date
        self.priceUSD = price_usd
        self.priceFX = price_fx
        self.taxableIncomeUSD = taxableIncome_usd
        self.taxableIncomeFX = taxableIncome_fx        
    
    def __repr__(self):
        return f'{self.address} - {self.balance} - {self.date} - {self.priceUSD} - {self.priceFX} - {self.taxableIncomeUSD} - {self.taxableIncomeFX}'
    
    @staticmethod
    def get_all():
        return pls_wallet_history.query.all()
    
    @staticmethod
    def new_balance(address, balance, price_usd, price_fx, taxableIncome_usd, taxableIncome_fx):
        my_balance = pls_wallet_history(
            address = address,
            balance = balance,
            date = datetime.now(),
            price_usd=price_usd,
            price_fx=price_fx,
            taxableIncome_usd=taxableIncome_usd,
            taxableIncome_fx=taxableIncome_fx
        )
        db.session.add(my_balance)
        db.session.commit()

class pls_price(db.Model):
    '''
    PLS price history
    '''
    __tablename__ = 'pls_price'
    id = db.Column('id', db.Integer, primary_key = True)
    date = db.Column('date', db.DateTime, nullable = False)
    priceUSD = db.Column('priceUSD', db.Float, nullable = False)
    priceFX = db.Column('priceFX', db.Float, nullable = True)
    
    def __init__(self, date, priceUSD, priceFX):
        self.date = date
        self.priceUSD = priceUSD
        self.priceFX = priceFX
        
    def __repr__(self):
        return f'{self.date} - {self.priceUSD} - {self.priceFX}'
    
    @staticmethod
    def get_last():
        return pls_price.query.order_by(pls_price.date.desc()).first()
    
    @staticmethod
    def store_new_price(valueUSD, valueFX):
        new_price = pls_price(datetime.now(), valueUSD, valueFX)
        db.session.add(new_price)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return pls_price.query.order_by(pls_price.date.asc()).all()

class pls_block_explorer(db.Model):
    '''
    PLS Block explorer scanner status
    '''
    id = db.Column('id', db.Integer, primary_key = True)
    blockheight = db.Column('blockheight', db.Integer, nullable = False)
    date = db.Column('date', db.DateTime, nullable = False)
    
    def __init__(self, blockheight, date):
        self.blockheight = blockheight
        self.date = date
        
    def __repr__(self):
        return f'{self.blockheight} - {self.date}'
    
    def new_block(self, blockheight):
        new_block = pls_block_explorer(blockheight=blockheight,date = datetime.now())
        db.session.add(new_block)
        db.session.commit()
    
    @staticmethod
    def get_last():
        return pls_block_explorer.query.order_by(pls_block_explorer.date.desc()).first()

class pls_validator_withdrawals(db.Model):
    '''
    PLS Validators data
    '''
    __tablename__ = 'pls_validator_withdrawals'
    index = db.Column('index', db.Integer, primary_key = True)
    validatorIndex = db.Column('validatorIndex', db.Integer, nullable = False)
    blockNumber = db.Column('blockNumber', db.Integer, nullable = False)
    address = db.Column('address', db.String(100), nullable = False)
    miner = db.Column('miner', db.String(100), nullable = False)
    amount = db.Column('amount', db.Float, nullable = False)
    timeStamp = db.Column('timeStamp', db.DateTime, nullable = False)
    priceUSD = db.Column('priceUSD', db.Float, nullable = True)
    priceFX = db.Column('priceFX', db.Float, nullable = True)
    
    def __init__(self, index, validatorIndex, blockNumber, address, miner, amount, timeStamp, priceUSD, priceFX):
        self.index = index
        self.validatorIndex = validatorIndex
        self.blockNumber = blockNumber
        self.address = address
        self.miner = miner
        self.amount = amount
        self.timeStamp = timeStamp
        self.priceUSD = priceUSD
        self.priceFX = priceFX
        
    def __repr__(self):
        return f'{self.index} - {self.validatorIndex} - {self.blockNumber} - {self.address} - {self.miner} - {self.amount} - {self.timeStamp} - {self.priceUSD} - {self.priceFX}'
    
    @staticmethod
    def get_all():
        return pls_validator_withdrawals.query.all()
    
    @staticmethod
    def get_all_by_address(address):
        return pls_validator_withdrawals.query.filter_by(address=address).all()
    
    @staticmethod
    def get_one_by_index(index):
        return pls_validator_withdrawals.query.filter_by(index=index).first()
    
    @staticmethod
    def get_all_by_validatorIndex(validatorIndex):
        return pls_validator_withdrawals.query.filter_by(validatorIndex=validatorIndex).all()
    
    @staticmethod
    def get_all_no_priceUSD():
        return pls_validator_withdrawals.query.filter_by(priceUSD=None).all()
    
    @staticmethod
    def get_all_no_priceFX():
        return pls_validator_withdrawals.query.filter_by(priceFX=None).all()
    
    @staticmethod
    def get_not_in_share_by_wallet(wallet):
        # get all withdrawals for the current wallet address that are not in the registered_blocks
        registered_withdrawals = pls_share_details.query.with_entities(pls_share_details.whitdrawal_id).all()
        pending_whitdrawals = []
        user_whitdrawals = pls_validator_withdrawals.query.filter_by(address=wallet).all()
        for user_whitdrawal_data in user_whitdrawals:
            if user_whitdrawal_data.index not in registered_withdrawals:
                pending_whitdrawals.append(user_whitdrawal_data)
        return pending_whitdrawals
        
class task_list(db.Model):
    '''
    Task list table
    '''
    __tablename__ = 'task_list'
    id = db.Column('id', db.Integer, primary_key = True)
    task_name = db.Column('task_name', db.String(100), nullable = False)
    task_description = db.Column('task_description', db.String(100), nullable = True)
    task_type = db.Column('task_type', db.String(100), nullable = False)

    def __init__(self, task_name, task_description, task_type):
        self.task_name = task_name
        self.task_description = task_description
        self.task_type = task_type

    def __repr__(self):
        return f'{self.task_name} - {self.task_description} - {self.task_type}'

    @staticmethod
    def get_all():
        return task_list.query.all()

    @staticmethod
    def get_model(name):
        return task_list.query.filter_by(task_name=name).first()

class task_scheduler(db.Model):
    '''
    Task scheduler table
    '''
    __tablename__ = 'task_scheduler'
    id = db.Column('id', db.Integer, primary_key = True)
    task_id = db.Column('task_id', db.Integer, db.ForeignKey('task_list.id'), nullable = False)
    task_rel = db.relationship('task_list', backref=db.backref('task_scheduler', lazy=True))
    task_cron = db.Column('task_cron', db.String(100), nullable = False)
    task_active = db.Column('task_active', db.Boolean, nullable = False, default = True)
    task_worker_id = db.Column('task_worker_id', db.Text, nullable = True)
    task_last_run = db.Column('task_last_run', db.DateTime, nullable = True)

    def __init__(self, task_id, task_cron, task_active, task_worker_id, task_last_run):
        self.task_id = task_id
        self.task_cron = task_cron
        self.task_active = task_active
        self.task_worker_id = task_worker_id
        self.task_last_run = task_last_run

    def __repr__(self):
        return f'{self.task_id} - {self.task_cron} - {self.task_active}'

    @staticmethod
    def get_all():
        return task_scheduler.query.all()

    @staticmethod
    def get_one_by_id(id):
        return task_scheduler.query.filter_by(id=id).first()
    
    @staticmethod
    def get_one_by_worker_id(worker_id):
        return task_scheduler.query.filter_by(task_worker_id=worker_id).first()
    
    @staticmethod
    def get_task_by_name(name):
        task_id = task_list.query.filter_by(task_name=name).first()
        return task_scheduler.get_one_by_id(task_id.id)

    @staticmethod
    def get_active():
        return task_scheduler.query.filter_by(task_active=True).all()
    
    @staticmethod
    def get_inactive():
        return task_scheduler.query.filter_by(task_active=False).all()
    
class pls_share_seq(db.Model):
    '''
    PLS share sequencer - controls share sequence using timestamps
    '''
    __tablename__ = 'pls_share_idx'
    index = db.Column('index', db.Integer, primary_key = True)
    timeStamp = db.Column('timeStamp', db.DateTime, nullable = False)
    pls_address = db.Column('pls_address', db.String(100), nullable = False)
    pls_sequence = db.Column('pls_sequence', db.String(100), nullable = False)
    
    def __init__(self, timeStamp, pls_address, pls_sequence):
        self.timeStamp = timeStamp
        self.pls_address = pls_address
        self.pls_sequence = pls_sequence
        
    def __repr__(self):
        return f'{self.index} - {self.timeStamp} - {self.pls_address} - {self.pls_sequence}'
    
    @staticmethod
    def new_sequence(pls_address, tailer):
        wallet = pls_wallets.get_one_by_address(pls_address)
        try:
            owner = wallet.owner
            timeStamp = datetime.now()
            # create a sequence string using this format: <wallet_owner>_<YYYY/MM/DD>
            sequence_string = f'{owner}_{timeStamp.strftime("%Y/%m/%d")}_{tailer}'
            my_sequence = pls_share_seq(timeStamp, pls_address, sequence_string)
            db.session.add(my_sequence)
            db.session.commit()
            return my_sequence
        except Exception as e:
            return None            

    @staticmethod
    def get_all():
        return pls_share_seq.query.all()
    
    @staticmethod
    def get_sequence_by_address(pls_address):
        return pls_share_seq.query.filter_by(pls_address=pls_address).all()
    
class pls_share(db.Model):
    '''
    PLS share header - Controls payment orders to project manager.
    '''
    __tablename__ = 'pls_share'
    index = db.Column('index', db.Integer, primary_key = True)
    share_sequence = db.Column('share_sequence', db.Integer, db.ForeignKey('pls_share_idx.index'), nullable = True)
    timeStamp = db.Column('timeStamp', db.DateTime, nullable = False)
    pls_wallet_payer = db.Column('pls_wallet_payer', db.String(100), nullable = False)
    pls_wihdrawed = db.Column('pls_wihdrawed', db.Float, nullable = False)
    pls_payable_amount = db.Column('pls_payable_amount', db.Float, nullable = False)
    trx_pay_date = db.Column('trx_pay_date', db.DateTime, nullable = True)
    trx_hash = db.Column('trx_hash', db.String(100), nullable = True)
    priceUSD = db.Column('priceUSD', db.Float, nullable = True)
    priceFX = db.Column('priceFX', db.Float, nullable = True)
    approved = db.Column('approved', db.Boolean, nullable = False, default = True)
    paid = db.Column('paid', db.Boolean, nullable = False, default = False)
    
    def __init__(self, share_sequence, timeStamp, pls_wallet_payer, pls_withdrawed, pls_payable_amount, trx_pay_date, trx_hash, priceUSD, priceFX, approved, paid):
        self.share_sequence = share_sequence
        self.timeStamp = timeStamp
        self.pls_wallet_payer = pls_wallet_payer
        self.pls_wihdrawed = pls_withdrawed
        self.pls_payable_amount = pls_payable_amount
        self.trx_pay_date = trx_pay_date
        self.trx_hash = trx_hash
        self.priceUSD = priceUSD
        self.priceFX = priceFX
        self.approved = approved
        self.paid = paid
    
    def __repr__(self):
        return f'{self.index} - {self.share_sequence} - {self.timeStamp} - {self.pls_wallet_payer} - {self.pls_wihdrawed} - {self.pls_payable_amount} - {self.trx_pay_date} - {self.trx_hash} - {self.priceUSD} - {self.priceFX} - {self.approved} - {self.paid}'
    
    @staticmethod
    def new_header(share_sequence, pls_wallet_payer, pls_withdrawed, pls_payable_amount, priceUSD, priceFX):
        new_share = pls_share(share_sequence, datetime.now(), pls_wallet_payer, pls_withdrawed, pls_payable_amount, None, None, priceUSD, priceFX, True, False)
        db.session.add(new_share)
        db.session.commit()
        return new_share
    
    @staticmethod
    def set_paid_by_wallet(sequence, wallet, trx_hash):
        share = pls_share.query.filter_by(share_sequence=sequence, pls_wallet_payer=wallet).first()
        share.paid = True
        share.trx_hash = trx_hash
        share.trx_pay_date = datetime.now()
        db.session.commit()
        return share
    
    @staticmethod
    def get_all():
        return pls_share.query.all()
    
    @staticmethod
    def get_pay_pending():
        return pls_share.query.filter_by(paid=False).all()
    
    @staticmethod
    def get_pay_pending_by_wallet(wallet):
        return pls_share.query.filter_by(pls_wallet_payer=wallet, paid=False).all()
    
    @staticmethod
    def get_approved():
        return pls_share.query.filter_by(approved=True).all()
    
    @staticmethod
    def get_approved_by_wallet(wallet):
        return pls_share.query.filter_by(pls_wallet_payer=wallet, approved=True).all()
    
    @staticmethod
    def get_not_approved():
        return pls_share.query.filter_by(approved=False).all()
    
    @staticmethod
    def get_not_approved_by_wallet(wallet):
        return pls_share.query.filter_by(pls_wallet_payer=wallet, approved=False).all()
    
    @staticmethod
    def set_approved_by_wallet(sequence, wallet):
        share = pls_share.query.filter_by(share_sequence=sequence, pls_wallet_payer=wallet).first()
        share.approved = True
        db.session.commit()
        return share
    
    @staticmethod
    def set_not_approved_by_wallet(sequence, wallet):
        share = pls_share.query.filter_by(share_sequence=sequence, pls_wallet_payer=wallet, paid=False).first()
        try:
            share.approved = False
            db.session.commit()
            return share
        except Exception as e:
            return None

            
class pls_share_details(db.Model):
    '''
    PLS share detail - all related movements for each wallet.
    '''
    __tablename__ = 'pls_share_details'
    index = db.Column('index', db.Integer, primary_key = True)
    share_sequence = db.Column('share_sequence', db.Integer, db.ForeignKey('pls_share_idx.index'), nullable = True)
    pls_wallet_payer = db.Column('pls_wallet_payer', db.String(100), nullable = False)
    whitdrawal_id = db.Column('whitdrawal_id', db.Integer, db.ForeignKey('pls_validator_withdrawals.index'), nullable = False)
    validatorIndex = db.Column('validatorIndex', db.Integer, nullable = False)
    blockNumber = db.Column('blockNumber', db.Integer, nullable = False)
    timeStamp = db.Column('timeStamp', db.DateTime, nullable = False)
    whitdrawed_amount = db.Column('whitdrawed_amount', db.Float, nullable = False)
    approved = db.Column('approved', db.Boolean, nullable = False, default = True)
    share_pct = db.Column('share_pct', db.Float, nullable = False)
    share_amount = db.Column('share_amount', db.Float, nullable = False)
    share_requested_date = db.Column('share_requested_date', db.DateTime, nullable = True)
    share_paid = db.Column('trx_paid', db.Boolean, nullable = False, default = False)
    
    def __init__(self, share_sequence, pls_wallet_payer, whitdrawal_id, validatorIndex, blockNumber, timeStamp, whitdrawed_amount, approved, share_pct, share_amount, share_requested_date, share_paid):
        self.share_sequence = share_sequence
        self.pls_wallet_payer = pls_wallet_payer
        self.whitdrawal_id = whitdrawal_id
        self.validatorIndex = validatorIndex
        self.blockNumber = blockNumber
        self.timeStamp = timeStamp
        self.whitdrawed_amount = whitdrawed_amount
        self.approved = approved
        self.share_pct = share_pct
        self.share_amount = share_amount
        self.share_requested_date = share_requested_date
        self.share_paid = share_paid
        
    def __repr__(self):
        return f'{self.index} - {self.share_sequence} - {self.pls_wallet_payer} - {self.whitdrawal_id} - {self.validatorIndex} - {self.blockNumber} - {self.timeStamp} - {self.whitdrawed_amount} - {self.approved} - {self.share_pct} - {self.share_amount} - {self.share_requested_date} - {self.share_paid}'
    
    
    @staticmethod
    def new_detail(share_sequence, pls_wallet_payer, whitdrawal_id, validatorIndex, blockNumber, timeStamp, whitdrawed_amount, share_pct, share_amount):
        new_detail = pls_share_details(share_sequence, pls_wallet_payer, whitdrawal_id, validatorIndex, blockNumber, timeStamp, whitdrawed_amount, True, share_pct, share_amount, datetime.now(), False)
        db.session.add(new_detail)
        db.session.commit()
        return new_detail
    
    @staticmethod
    def return_total_by_sequence(share_sequence):
        return pls_share_details.query.filter_by(share_sequence=share_sequence).sum(pls_share_details.share_amount)
    
    @staticmethod
    def set_requested(share_sequence, pls_wallet_payer, share_requested_date):
        share = pls_share_details.query.filter_by(share_sequence=share_sequence, pls_wallet_payer=pls_wallet_payer).first()
        share.share_requested_date = share_requested_date
        db.session.commit()
        return share
    
    @staticmethod
    def set_paid(share_sequence, pls_wallet_payer):
        share = pls_share_details.query.filter_by(share_sequence=share_sequence, pls_wallet_payer=pls_wallet_payer).first()
        share.share_paid = True
        db.session.commit()
        return share
    
    @staticmethod
    def set_unapproved(share_sequence, pls_wallet_payer):
        share = pls_share_details.query.filter_by(share_sequence=share_sequence, pls_wallet_payer=pls_wallet_payer, share_paid=False).first()
        try:
            share.approved = False
            db.session.commit()
            return share
        except Exception as e:
            return None
    
    @staticmethod
    def set_approved(share_sequence, pls_wallet_payer):
        share = pls_share_details.query.filter_by(share_sequence=share_sequence, pls_wallet_payer=pls_wallet_payer).first()
        share.approved = True
        db.session.commit()
        return share
    
    @staticmethod
    def get_all_by_wallet_and_sequence(share_sequence, pls_wallet_payer):
        return pls_share_details.query.filter_by(share_sequence=share_sequence, pls_wallet_payer=pls_wallet_payer).all()
    
        
        
    
    