#############################################
# site.py
# (c)2023, Raskitoma.com
#--------------------------------------------
# Master Routes
#-------------------------------------------- 
# Getting libraries
import json
import locale
from app import datetime, logging, get_timestamp, token, login_manager, app_config, dump_datetime, db, app_settings
from .utl import user_login as login
from .utl import get_data_from_response, generate_uuid ,generate_api_response, err_json, mail_send
from .models import Users
from .models import logs
from sqlalchemy import func
from .str import LOG_ALERT, LOG_ERROR, LOG_INFO, LOG_WARNING, LOG_DEBUG
from .str_mail import MAIL_FORGOT, MAIL_FORGOT_SUBJECT, MAIL_OTP, MAIL_OTP_SUBJECT, MAIL_FORGOT
from flask import flash, request, jsonify, render_template, make_response, send_file, session, send_from_directory, redirect, current_app, Blueprint, url_for
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

# constants
TEMPLATE_LOGIN = 'login.html'
TEMPLATE_MAIL = 'mail_confirm.html'
TEMPLATE_REGISTER = 'register.html'
SECTION_CONFIRM = 'Confirm email.'
ERROR_DATA_SAVE = "Error saving data: {}"

# bp definition
site_bp = Blueprint('site', __name__, template_folder='templates')

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(current_app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(user_id)
   
# ##########################################################
# Site routes

# Home
@site_bp.route('/')
def home():
    app_config_data = app_config()
    # redirect to /admin if site is not enabled
    if app_settings()['ADMIN_ONLY']:
        return redirect(url_for('admin.index'))
    
    if not session.get('logged_in') or session.get('suid') is None:
        return render_template(TEMPLATE_LOGIN,
                app_config = app_config_data,
                section = 'Login',
            )
    else:
        user_data = Users.query.filter_by(id=session['suid']).first()
        if not user_data.verified_status:
            return make_response(render_template(TEMPLATE_MAIL,
                    app_config = app_config_data,
                    section = SECTION_CONFIRM,
                    user_data = user_data,
                    token = token
                ), 200, {'Access-Control-Allow-Origin': '*'})
        
        current_time = datetime.now()
        # select current stage
        
        return make_response(render_template('index.html',
                app_config = app_config_data,
                section = 'Home',
                user_data = user_data,
                token = token
            ), 200, {'Access-Control-Allow-Origin': '*'})  
          
# Login
@site_bp.route('/login', methods=['POST'])
def loginme():
    # get posted data from form
    username = request.form['username']
    password = request.form['password']
    login_details = {
        'username': username,
        'password': password
    }
    result = login(login_details=login_details)
    response = get_data_from_response(result)
    if result.status_code != 200:
        category = 'danger'
        message = response['message']
        flash(message, category)
        return make_response(render_template(TEMPLATE_LOGIN,
                app_config = app_config(),
                section = 'Login',
                token = token
            ), 200, {'Access-Control-Allow-Origin': '*'})  
    return redirect('/')
# Logout
@site_bp.route('/logout')
def logout():
    session['logged_in'] = False
    # destroy session
    session.clear()
    return redirect('/')
