#############################################
# core.py
# (c)2023, Raskitoma.com
#--------------------------------------------
# Master APP
#-------------------------------------------- 
import os, sys
import logging
import influxdb_client
from flask import Flask, request, render_template, current_app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_adminlte3 import AdminLTE3
import flask_admin as admin
import flask_login as login
from flask_login import LoginManager
from flask_mailman import Mail
from flask_migrate import Migrate
from flask_cors import CORS
from logging.handlers import SysLogHandler, SMTPHandler
from rfc5424logging import Rfc5424SysLogHandler
from influxdb_client.client.write_api import SYNCHRONOUS

# Initializing
# Loading modules
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
adminlte = AdminLTE3()

# globals
global my_app_config

# some config variables
HEADER_01_KEY = 'Access-Control-Allow-Origin'
HEADER_01_VAL = '*'
token = None

settings_module = os.getenv('APP_SETTINGS_MODULE')

# ###############################
# Some usefull functions
# ###############################
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(current_app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        from app.rskcore.models import Users
        return Users.query.get(user_id)

def app_config():
    return {
        'app_name' : current_app.config['ADMIN_NAME'],
        'app_copy' : current_app.config['ADMIN_FOOTER'],
        'app_favi' : current_app.config['ADMIN_FAVICON'],
        'app_logo' : current_app.config['ADMIN_LOGO'],
        'app_supp' : current_app.config['MAIL_ADMIN'],
        'otp_expire' : current_app.config['OTP_EXPIRE']
    }
    
def app_settings():
    return current_app.config
    
def register_error_handlers(app):

    @app.errorhandler(500)
    def base_error_handler(e):
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def error_404_handler(e):
        return render_template('404.html'), 404

    @app.errorhandler(401)
    def error_404_handler(e):
        return render_template('401.html'), 401
    
    @app.errorhandler(403)
    def error_403_handler(e):
        return render_template('403.html'), 403
    
    
def get_timestamp():
    '''
    Just a simple function to retrieve a formatted timestamp.
    '''
    return datetime.now().strftime(('%Y-%m-%d %H:%M:%S'))

def dump_datetime(value):
    '''
    Deserialize datetime object into string form for JSON processing
    '''
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")

def twotimes(value):
    if value is None:
        return None
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

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
    
def configure_logging(app):
    '''
    Config log handlers for Flask app
    :param app: Flask instance app
    '''

    # Remove default handlers
    del app.logger.handlers[:]

    loggers = [app.logger, ]
    handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(verbose_formatter())

    if (app.config['APP_ENV'] == app.config['APP_ENV_LOCAL']) or (
            app.config['APP_ENV'] == app.config['APP_ENV_TESTING']) or (
            app.config['APP_ENV'] == app.config['APP_ENV_DEVELOPMENT']):
        console_handler.setLevel(logging.DEBUG)
        handlers.append(console_handler)
    elif app.config['APP_ENV'] == app.config['APP_ENV_PRODUCTION']:
        console_handler.setLevel(logging.INFO)
        handlers.append(console_handler)

        mail_handler = SMTPHandler((app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                   app.config['DONT_REPLY_FROM_EMAIL'],
                                   app.config['ADMINS'],
                                   '[Error][{}] La aplicación falló'.format(app.config['APP_ENV']),
                                   (app.config['MAIL_USERNAME'],
                                    app.config['MAIL_PASSWORD']),
                                   ())
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(mail_handler_formatter())
        handlers.append(mail_handler)
        
        if app.config['SYSLOG_URI'] is not None:
            try:
                mysyslog = Rfc5424SysLogHandler(address=(app.config['SYSLOG_URI'], int(app.config['SYSLOG_PORT'])))
                handlers.append(mysyslog)
            except Exception as e:
                print(str(e))

    for l in loggers:
        for handler in handlers:
            l.addHandler(handler)
        l.propagate = False
        l.setLevel(logging.DEBUG)


def mail_handler_formatter():
    return logging.Formatter(
        '''
            Message type:       %(levelname)s
            Location:           %(pathname)s:%(lineno)d
            Module:             %(module)s
            Function:           %(funcName)s
            Time:               %(asctime)s.%(msecs)d
            Message:
            %(message)s
        ''',
        datefmt='%d/%m/%Y %H:%M:%S'
    )


def verbose_formatter():
    return logging.Formatter(
        '[%(asctime)s.%(msecs)d]\t %(levelname)s \t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )

# ###############################
# Create the application instance ++++ APP Creation
# ###############################
def create_app(settings_module):
    app = Flask(__name__, instance_relative_config=True, static_folder='templates/assets')
    app.config.from_object(settings_module)
    if app.config.get('TESTING', False):
        app.config.from_pyfile('config-testing.py', silent=True)
    else:
        app.config.from_pyfile('config.py', silent=True)    

    configure_logging(app)

    # CORS fix
    CORS(app)

    # Login manager init
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
        
    # Init up modules
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    adminlte.init_app(app)

    # customizing error handlers
    register_error_handlers(app)
   
    from app.rskcore.site import site_bp

    app.register_blueprint(site_bp)
   
    return app

#############################################
# EoF
