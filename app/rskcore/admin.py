#############################################
# admin.py
# (c)2023, Raskitoma.com
#--------------------------------------------
# Master Admin for Core using adminLTE Theme
#-------------------------------------------- 
from datetime import timedelta
import io
import locale
import os
import typing
import uuid
from flask import jsonify, url_for, redirect, render_template, \
    request, flash, session, abort, current_app, make_response, \
    send_file
import requests
from sqlalchemy import false
from app import db, adminlte, datetime, init_login, \
    str_to_bool, login_manager
from .models import Users, master_config
from .models import logs, sysalerts
from .models import pls_wallets, pls_validator_withdrawals, pls_price
from .models import task_scheduler, task_list
from .models import pls_share_seq, pls_share, pls_share_details
from .utl import generate_uuid, user_login, logout as user_logout, \
    get_data_from_response, new_log, \
    monthdiff, get_var_value, rand_string
from wtforms import form, fields, validators, widgets, TextAreaField, RadioField, ValidationError
from markupsafe import Markup
from .str_log import *
import wtforms_json
import logging
import json
import flask_admin as admin
import flask_login as login
import gettext
from urllib import parse
import email_validator
from redis import Redis
from flask_admin.actions import action
from flask_admin.contrib import sqla, rediscli
from flask_admin.form import DateTimePickerWidget, fields as admin_fields, rules
from flask_admin.model.template import TemplateLinkRowAction
from flask_admin import helpers, expose, BaseView
from flask_admin.menu import MenuLink, MenuView, BaseMenu
from werkzeug.security import generate_password_hash, check_password_hash
from ..scheduler import get_tasks

# Defining constants
C_LOGIN_VIEW = '.login_view'
C_INDEX_VIEW = '.index'
C_NO_PRIVILEGES = 'You do not have privileges to use this feature'
C_REL_USERS_MAIL = 'users.email'
TIME_FORMAT_ARGS = '%Y-%m-%d %H:%M'
TIME_FORMAT_PRES = 'YYYY-MM-DD HH:mm:ss'
TIME_CONTRACT_ARGS = '%Y-%m-%d'

logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

wtforms_json.init()

app = current_app

# accesing app config
myconfig = current_app.config

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(user_id)

# Form definitions
class LoginForm(form.Form):
    username = fields.StringField(validators=[validators.DataRequired()])
    password = fields.PasswordField(validators=[validators.DataRequired()])
    def validate_login(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('Invalid user')
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid password')
    def get_user(self):
        return Users.get_by_email(self.username.data)

class RegistrationForm(form.Form):   
    username = fields.StringField('Create User', validators=[validators.DataRequired()])
    password = fields.PasswordField('Create Password', validators=[validators.DataRequired(), validators.equal_to('confirm', message='Passwords must match')])
    confirm = fields.PasswordField('Repeat Password', validators=[validators.DataRequired(), validators.equal_to('password', message='Passwords must match')])
    fullname = fields.StringField('Full Name', validators=[validators.DataRequired()])
    email = fields.StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    def validate_login(self, field):
        if Users.query.filter_by(username=self.username.data).count() > 0:
            raise validators.ValidationError('Duplicate username')

# Some functions
def set_template_objects(self):
    self._template_args['site_logo'] = myconfig['ADMIN_LOGO']
    self._template_args['site_name'] = myconfig['ADMIN_NAME']
    self._template_args['site_favicon'] = myconfig['ADMIN_FAVICON']
    self._template_args['site_description'] = myconfig['ADMIN_DESC']
    self._template_args['site_footer'] = myconfig['ADMIN_FOOTER']

def validate_data_required(form, field):
    if field.data is None:
        raise ValidationError('This field is required')

def validate_non_negative(form, field):
    if field.data is None:
        return
    if field.data < 0:
        raise ValidationError('Value must be non-negative')

def validate_non_negative_only(form, field):
    if field.data not in (None, '') and field.data < 0:
        raise ValidationError('Value must be non-negative')

def validate_zero(form, field):
    if field.data is None:
        return
    if field.data < 0:
        raise ValidationError('Value must be non-negative')
    elif field.data == 0:
        field.data = 0
        
def validate_range(form, field, min, max):
    if field.data is None:
        return
    if field.data < min or field.data > max:
        raise ValidationError(f'Value must be between {min} and {max}')
        
def get_dash_data():
    dash_data = {}
    # get current date
    current_date = datetime.now()
    
    # set date as string for url
    current_date_str = current_date.strftime('%Y-%m-%d 00:00:00')
    current_date_url = parse.quote(current_date_str)
    url_expired = f'/admin/contract/?flt1_14={current_date_url}'
       
    # assembling data
    dash_data['data_contracts'] = {}
    dash_data['data_contracts_qty'] = 0
    dash_data['expiring_qty'] = 0
    dash_data['expired_qty'] = 0
    dash_data['data_tenants_individuals_qty'] = 0
    dash_data['data_tenants_business_qty'] = 0
    dash_data['date_today'] = current_date
    dash_data['date_expiring'] = current_date + timedelta(days=30)
    dash_data['all_docs_qty'] = 0
    
    return dash_data
 
# ###############################        
# Basic admin routes
class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(C_LOGIN_VIEW))
        self._template_args['dash_data'] = get_dash_data()
        set_template_objects(self)
        return super(MyAdminIndexView, self).index()

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            username = form.get_user()
            try:
                login_details = {
                    "username" : form.username.data,
                    "password" : form.password.data
                }
                response = user_login(login_details)
                if response.status_code == 200:
                    login.login_user(username)
                    logger.info('Login OK: {}'.format(form.username.data))
                    set_template_objects(self)
                else: 
                    flash('Login failed: {}'.format(get_data_from_response(response)["message"]), 'error')
                    logger.error('Login failed: {}'.format(get_data_from_response(response)["message"]))
            except Exception as e:
                flash('Login failed: {}'.format(e), 'error')
                logger.critical('Login failed: {}'.format(e))
        if login.current_user.is_authenticated:
            logger.info('Login OK: {}'.format(username.email))
            self._template_args['dash_data'] = get_dash_data()
            set_template_objects(self)            
            return super(MyAdminIndexView, self).index()
        link = '<br><hr><p>Get back to APP <a href="/">Click here to navigate.</a></p><hr><br>'
        self._template_args['form'] = form
        self._template_args['link'] = Markup(link)
        set_template_objects(self)
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        my_user = login.current_user
        logger.info('Logout OK: {}'.format(my_user))
        login.logout_user()
        user_logout(my_user)
        return redirect(url_for(C_LOGIN_VIEW))
    
# #########################################################################################################################################################################################################################
# #########################################################################################################################################################################################################################
# Custom Views
# #########################################################################################################################################################################################################################
# #########################################################################################################################################################################################################################
class tasks(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def tasks(self):
        if not login.current_user.is_authenticated or not login.current_user.is_admin:
            if not login.current_user.is_admin:
                flash(C_NO_PRIVILEGES, 'error')
            return redirect(url_for(C_INDEX_VIEW))
        # check if have been called via POST
        if request.method == 'GET':
            active_tasks = get_tasks() or {}
            inactive_tasks = get_tasks(mode='disabled') or {}
            self._template_args['active_tasks'] = active_tasks
            self._template_args['inactive_tasks'] = inactive_tasks
            set_template_objects(self)
            return self.render('myadmin3/tasks.html')

    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and login.current_user.is_admin
      
# #########################################################################################################################################################################################################################
# #########################################################################################################################################################################################################################
# Expanding Classes and Models
# #########################################################################################################################################################################################################################
# #########################################################################################################################################################################################################################
# Classes for extra objects
class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)
  
class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()  

class DividerMenu(BaseMenu):
    '''
        Bootstrap Menu divider item
    '''
    def __init__(self, name, class_name=None, icon_type=None, icon_value=None, target=None):
        super(DividerMenu, self).__init__(name, 'dropdown-divider pb-1 mb-2 invisible', icon_type, icon_value, target)

    def get_url(self):
        pass

    def is_visible(self):
        return True
      
# expand redis console for extra features
class RedisConsole(rediscli.RedisCli):
    def __init__(self, redis, menu_icon_type='fas', menu_icon_value='fa-database', menu_class_name='navbar-navy', **kwargs):
        super(RedisConsole, self).__init__(redis, **kwargs)
        self.menu_icon_type = menu_icon_type
        self.menu_icon_value = menu_icon_value
        self.menu_class_name = menu_class_name
        
    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.is_admin

      
# Set custom password and uuid fields for admin
class CustomPasswordField(fields.PasswordField): # If you don't want hide the password you can use a StringField
    def populate_obj(self, obj, name):
        setattr(obj, name, generate_password_hash(self.data)) # Password function

class CustomUUIDField(fields.StringField): 
    def populate_obj(self, obj, name):
        setattr(obj, name, generate_uuid())
        
class BootstrapRadioFieldWidget:
    def __init__(self, inline: bool = False, prefix_label: bool = True):
        self.inline = inline
        self.prefix_label = prefix_label
        
    def __call__(self, field: fields.RadioField, **kwargs: typing.Any) -> Markup:
        kwargs.setdefault('id', field.id)
        html = []
        if self.inline:
            template = '<label class="radio-inline ml-2">{0} {1}</label>'
        else:
            template = '<div class="radio"><label>{0} {1}</label></div>'
        for subfield in field:
            checked = ' checked' if field.data == subfield._value() else ''
            subfield_html = f'<input type="radio" name="{field.name}" value="{subfield._value()}" id="{subfield.id}"{checked}>'
            if self.prefix_label:
                html.append(template.format(subfield.label, subfield_html))
            else:
                html.append(template.format(subfield_html, subfield.label))
        return Markup(''.join(html))
      
class BootstrapRadioField(fields.RadioField):
    widget = BootstrapRadioFieldWidget(prefix_label=False, inline=True)


# ####################################
# Class for std model
class ModelSTD(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    column_auto_select_related = True
    can_set_page_size = True
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']

    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and login.current_user.is_admin

    @property        
    def can_create(self):
        return login.current_user.is_admin

    @property        
    def can_edit(self):
        return login.current_user.is_admin

    @property        
    def can_delete(self):
        return login.current_user.is_admin

    # editing form actions to save log
    def create_model(self, form):
        log2store = LOG_CREATE % (login.current_user.email, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
        return super().create_model(form)
        
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        return super().update_model(form, model)
    
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)

# ####################################
# Class for show only permissions
class ModelShow(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    can_delete = False
    can_create = False
    can_edit = False
    can_set_page_size = True
    column_auto_select_related = True
    def is_accessible(self):
        return login.current_user.is_authenticated and (login.current_user.is_staff or login.current_user.is_admin)
    
    # editing form actions to save log
    def create_model(self, form):
        log2store = LOG_CREATE % (login.current_user.email, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
        return super().create_model(form)
        
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        return super().update_model(form, model)
    
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)
    
# ####################################
# Class for OTP
class ModelOTP(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    can_delete = False
    can_create = False
    can_edit = False
    can_set_page_size = True
    column_auto_select_related = True
    column_searchable_list = ['requester', 'consumed', 'valid', 'created_at', 'expires_at']
    column_exclude_list = ['password', 'public_id']
    column_filters = ['requester', 'consumed', 'valid', 'created_at', 'expires_at']    
    def is_accessible(self):
        return login.current_user.is_authenticated and (login.current_user.is_staff or login.current_user.is_admin)
    
    # editing form actions to save log
    def create_model(self, form):
        log2store = LOG_CREATE % (login.current_user.email, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
        return super().create_model(form)
        
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        return super().update_model(form, model)
    
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)

# ####################################
# Class for user model
class ModelUsers(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    can_set_page_size = True    
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']
    column_exclude_list = ['password']
    column_searchable_list = ['email', 'fullname']
    column_list = ['created_at', 'modified_at', 'email', 'fullname', 'verified', 'staff', 'admin', 'active', 'access']
    column_editable_list = ['email', 'fullname', 'verified', 'staff', 'admin', 'active']
    column_filters = ['email', 'fullname', 'created_at', 'modified_at' , 'verified', 'staff', 'admin']
    column_auto_select_related = True
    form_columns = ['email', 'password', 'fullname', 'admin', 'staff', 'access', 'verified', 'active']
    form_excluded_columns = ['otp', 'log', 'created_at', 'modified_at', 'contract', 'users', 'users_logs', 'users_otp']
    column_formatters = {
        'created_at': lambda v, c, m, p: m.created_at.strftime(TIME_FORMAT_ARGS),
        'modified_at': lambda v, c, m, p: m.modified_at.strftime(TIME_FORMAT_ARGS),
        'verified': lambda v, c, m, p: m.verified.strftime(TIME_FORMAT_ARGS) if m.verified else 'Not verified',
        'access': lambda v, c, m, p: m.access if m.access else 'No access'
    }
    form_widget_args = {
        'verified': {
            'data-datetime-format': TIME_FORMAT_PRES,
            'readonly': False,
            'visible': False, 
            'default': datetime.now()
        },
        'access' : {
            'rows': 10,
            'cols': 100,
            'style': 'width: 100%; height: 100%; font-family: monospace;',
            'readonly': False,
            'visible': True
        }   
    }
    
    form_extra_fields = {
        'email': fields.EmailField('Email/User', validators=[validators.DataRequired(), validators.Email()], render_kw={'placeholder': 'Email/User', 'autocomplete': 'new-password'}),
        'password': fields.PasswordField(
            'Password', 
            render_kw={'placeholder': 'Password', 'autocomplete': 'new-password'},
            description='Left blank if you don\'t want to change it, input the new password to change it'),
        'fullname': fields.StringField('Full Name', validators=[validators.DataRequired()]),
        'admin': fields.BooleanField('Is Admin?', default=False),
        'staff': fields.BooleanField('Is Staff?', default=False),        
        'active' : fields.BooleanField('Is Active?', default=True),
        'verified': fields.DateTimeField('Verified date', default=datetime.now(), widget = DateTimePickerWidget()),
        'access' : fields.TextAreaField('Access', description='JSON formatted access list', default='{}'),
    }

    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and login.current_user.is_admin
    
    # filter results based on user role
    def get_query(self):
        if login.current_user.is_admin:
            return self.session.query(self.model).filter(self.model.id != login.current_user.id)
        elif login.current_user.is_staff:
            return self.session.query(self.model).filter(self.model.id != login.current_user.id, self.model.admin == False, self.model.staff == False)

    @property        
    def can_create(self):
        return login.current_user.is_admin

    @property        
    def can_edit(self):
        return login.current_user.is_admin

    @property        
    def can_delete(self):
        return login.current_user.is_admin

    # editing form actions to save log
    def create_model(self, form):
        log2store = LOG_CREATE % (login.current_user.email, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
        user_obj = Users(
            created_at=datetime.now(),
            modified_at=datetime.now(),
            email=form.email.data,
            fullname=form.fullname.data,
            password=generate_password_hash(form.password.data),
            active=form.active.data,
            verified=form.verified.data,
            access=form.access.data,
            admin=form.admin.data,
            staff=form.staff.data
        )
        self.session.add(user_obj)
        self.session.commit()
        if login.current_user.is_admin:
            return self.session.query(self.model).filter(self.model.id != login.current_user.id)
        elif login.current_user.is_staff:
            return self.session.query(self.model).filter(self.model.id != login.current_user.id, self.model.admin == False, self.model.staff == False)
        
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        model.modified_at = datetime.now()
        model.email = form.email.data
        model.fullname = form.fullname.data
        if form.password.data:
            model.password = generate_password_hash(form.password.data)
        model.active = form.active.data
        model.verified = form.verified.data
        model.access = form.access.data
        model.admin = form.admin.data
        model.staff = form.staff.data
        self.session.commit()
        if login.current_user.is_admin:
            return self.session.query(self.model).filter(self.model.id != login.current_user.id)
        elif login.current_user.is_staff:
            return self.session.query(self.model).filter(self.model.id != login.current_user.id, self.model.admin == False, self.model.staff == False)
   
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)


# ####################################
# Class for logs
class ModelLogs(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    can_set_page_size = True
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']
    column_searchable_list = ['id', 'timestamp', 'users_rel.email', 'users_rel.fullname', 'module', 'severity', 'description', 'data']
    column_list = ['id', 'timestamp', 'users_rel.email', 'module', 'severity', 'description', 'data']
    column_filters = ['id', 'timestamp', Users.fullname, Users.email, 'module', 'severity', 'description', 'data']
    column_auto_select_related = True
    column_labels = {
        'users_rel.fullname': 'User Full Name',
        'users_rel.email': 'User',
    }
    column_formatters = {
        'timestamp': lambda v, c, m, p: m.timestamp.strftime(TIME_FORMAT_ARGS),
    }
    
    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and (login.current_user.is_staff or login.current_user.is_admin)

    @property        
    def can_create(self):
        return False

    @property        
    def can_edit(self):
        return False

    @property        
    def can_delete(self):
        return False

    def get_query(self):
        if login.current_user.is_admin:
            return self.session.query(self.model).order_by(self.model.timestamp.desc())
        elif login.current_user.is_staff:
            return self.session.query(self.model).filter(self.model.users_id == login.current_user.id).order_by(self.model.timestamp.desc())

# ####################################
# Class for alerts base
class ModelAlerts(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    can_set_page_size = True
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']
    column_searchable_list = ['id', 'created_at', 'modified_at', 'alert',
                              'alert_type', 'alert_status', 'alert_dismissed', 'alert_dismissed_at',
                              'alert_owner_rel.email' , 'alert_dismissed_by_rel.email']
    column_list = ['id', 'created_at', 'modified_at', 'alert',
                              'alert_type', 'alert_status', 'alert_dismissed', 'alert_dismissed_at',
                              'alert_owner_rel.email' , 'alert_dismissed_by_rel.email']
    column_filters = ['id', 'created_at', 'modified_at', 'alert',
                              'alert_type', 'alert_status', 'alert_dismissed', 'alert_dismissed_at',
                              'alert_owner_rel.email' , 'alert_dismissed_by_rel.email']
    column_auto_select_related = True
    column_labels = {
        'alert_owner_rel.email': 'Alert owned by',
        'alert_dismissed_by_rel.email': 'Dismissed by',
    }
    column_formatters = {
        'created_at': lambda v, c, m, p: m.created_at.strftime(TIME_FORMAT_ARGS),
        'modified_at': lambda v, c, m, p: m.created_at.strftime(TIME_FORMAT_ARGS),
    }
    
    @property        
    def can_create(self):
        return False

    @property        
    def can_edit(self):
        return False

    @property        
    def can_delete(self):
        return False

    def get_query(self):
        if login.current_user.is_admin:
            return self.session.query(self.model).order_by(self.model.created_at.desc())

# ####################################
# Class for alerts for admins
class ModelAlertsAdmin(ModelAlerts):
    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and login.current_user.is_admin
    
    @action('switch_alert', 'Switch alert status', 'Are you sure you want switch alert status?')
    def action_switch_alert(self, ids):
        try:
            query = self.model.query.filter(self.model.id.in_(ids)).all()
            for my_record in query:            
                prev_state = 'Dismissed' if my_record.alert_dismissed else 'Active'
                my_record.alert_dismissed = not my_record.alert_dismissed
                curr_state = 'Active' if my_record.alert_dismissed else 'Dismissed'
                my_record.alert_dismissed_by = login.current_user.id
                my_record.alert_dismissed_obs = f'Alert status switched from {prev_state} to {curr_state} by {login.current_user.email}'
                db.session.commit()
            log2store = LOG_BATCH % (login.current_user.email, 'Update', 'Alert status switched for ' + str(len(ids)) + ' record(s) - ' + str(ids))
            logger.warning(log2store)
            new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_BATCH}', data=log2store, image=None)
            flash(f'Alert switched for {str(len(ids))} record(s).', 'success')
        except Exception as e:
            if not self.handle_view_exception(e):
                raise
            flash(gettext('Failed to switch: %(error)s', error=str(e)), 'error')

# ####################################
# Class for alerts for users
class ModelAlertsUser(ModelAlerts):
    column_searchable_list = ['id', 'created_at', 'alert',
                              'alert_type', 'alert_status', 'alert_dismissed', 'alert_dismissed_at']
    column_list = ['id', 'created_at', 'alert',
                              'alert_type', 'alert_status', 'alert_dismissed', 'alert_dismissed_at']
    column_filters = ['id', 'created_at', 'alert',
                              'alert_type', 'alert_status', 'alert_dismissed', 'alert_dismissed_at']

    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and (login.current_user.is_staff or login.current_user.is_admin)
    def get_query(self):
        return self.session.query(self.model).filter(self.model.alert_owner == login.current_user.id).order_by(self.model.created_at.desc())
   
# ###############################
# Class for Config Vars
class ModelConfigVars(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']
    extra_js = []
    can_set_page_size = True
    column_searchable_list = []
    column_list = ['configname', 'configtype', 'configvalue', 'configstatus']
    column_exclude_list = []
    column_editable_list = ['configvalue', 'configstatus']
    column_filters = ['configname', 'configtype', 'configvalue', 'configstatus']
    column_formatters = {
        # 'configvalue': lambda v, c, m, p: Markup(f'<pre>{m.configvalue}</pre>'),
    }
    
    form_widget_args = {}
    column_labels = {
        'configname': 'Variable Name',
        'configtype': 'Type',
        'configvalue': 'Value',
        'configstatus': 'Status',
    }
    form_overrides = {
    }
    form_extra_fields = {
        'configname' : fields.StringField('Varible Name', validators=[validators.DataRequired()]),
        'configtype' : fields.SelectField('Type', choices=[('string', 'String'), ('int', 'Integer'), ('float', 'Float'), ('bool', 'Boolean'), ('list', 'List'), ('dict', 'Dictionary'), ('json', 'JSON')], validators=[validators.DataRequired()]),
        'configvalue' : fields.StringField('Value', validators=[validators.DataRequired()]),
        'configstatus' : fields.BooleanField('Status', default=True),
    }
        
    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and login.current_user.is_admin

    @property        
    def can_create(self):
        return login.current_user.is_admin

    @property        
    def can_edit(self):
        return login.current_user.is_admin

    @property        
    def can_delete(self):
        return login.current_user.is_admin

    # editing form actions to save log
    def create_model(self, form):
        log2store = LOG_CREATE % (login.current_user.email, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
        return super().create_model(form)
        
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        return super().update_model(form, model)
    
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)


# ###############################
# Class for PLS Wallets
class ModelPLSWallets(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']
    extra_js = []
    can_set_page_size = True
    column_searchable_list = []
    column_list = ['address', 'owner', 'balance']
    column_exclude_list = []
    column_editable_list = ['owner']
    column_filters = ['address', 'owner']
    column_formatters = {
        # 'configvalue': lambda v, c, m, p: Markup(f'<pre>{m.configvalue}</pre>'),
    }
    form_excluded_columns = ['balance', 'units']    
    form_widget_args = {}
    column_labels = {
        'configname': 'Variable Name',
        'configtype': 'Type',
        'configvalue': 'Value',
        'configstatus': 'Status',
    }
    form_overrides = {
    }
    form_extra_fields = {
        'address' : fields.StringField('Wallet Address', validators=[validators.DataRequired()]),
        'owner' : fields.StringField('Wallet Owner', validators=[validators.DataRequired()]),
    }
        
    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and login.current_user.is_admin

    @property
    def can_create(self):
        return login.current_user.is_admin

    # disabled editing
    @property        
    def can_edit(self):
        return False

    @property        
    def can_delete(self):
        return login.current_user.is_admin

    # editing form actions to save log
    def create_model(self, form):
        log2store = LOG_CREATE % (login.current_user.email, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
        pls_wallet_obj = pls_wallets(
            address=form.data['address'],
            owner=form.data['owner'],
            balance=0,
            units='PLS'
        )
        self.session.add(pls_wallet_obj)
        self.session.commit()
        return self.session.query(self.model)
        
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        return super().update_model(form, model)
    
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)


# ###############################
# Class for Tasks Scheduler
class ModelCroner(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']
    extra_js = []
    can_set_page_size = True
    column_searchable_list = []
    column_list = ['task_rel', 'task_cron', 'task_active', 'task_last_run', 'task_worker_id']
    column_exclude_list = []
    column_editable_list = ['task_active']
    column_filters = ['task_rel', 'task_cron', 'task_active']
    form_excluded_columns = ['task_worker_id', 'task_last_run']    
    form_widget_args = {}
    column_labels = {
        'task_rel': 'Task Name',
        'task_cron': 'Cron Like Schedule',
        'task_last_run': 'Last Run',
    }
    form_overrides = {
    }
    form_extra_fields = {
        'task_rel' : sqla.fields.QuerySelectField('Task Name', query_factory=lambda: task_list.get_all(), allow_blank=False, blank_text='(Select a Task)'),
        'task_cron' : fields.StringField('Cron Schedule', validators=[validators.DataRequired()]),
        'task_active' : fields.BooleanField('Active?', default=False),
    }
        
    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and login.current_user.is_admin

    @property
    def can_create(self):
        return login.current_user.is_authenticated and login.current_user.is_admin

    # disabled editing
    @property        
    def can_edit(self):
        return login.current_user.is_authenticated and login.current_user.is_admin

    @property        
    def can_delete(self):
        return login.current_user.is_authenticated and login.current_user.is_admin

    # editing form actions to save log
    def create_model(self, form):
        log2store = LOG_CREATE % (login.current_user.email, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
        new_task = task_scheduler(
            task_id=form.data['task_rel'].id,
            task_cron=form.data['task_cron'],
            task_active=form.data['task_active'],
            task_worker_id=None,
            task_last_run=None
        )
        self.session.add(new_task)
        self.session.commit()
        return self.session.query(self.model)
        
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        return super().update_model(form, model)
    
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)
    
    
# ###############################
# Class for Share payments
# ###############################
class ModelShareHeaders(sqla.ModelView):
    list_template = 'myadmin3/admin_std_list.html'
    create_modal = myconfig['ADMIN_MODAL']
    edit_modal = myconfig['ADMIN_MODAL']
    extra_js = []
    can_set_page_size = True
    column_searchable_list = []
    column_list = ['timeStamp', 'share_sequence', 'pls_wallet_payer', 'pls_payable_amount', 'trx_pay_date', 'trx_hash', 'priceUSD', 'priceFX', 'approved', 'paid']
    column_exclude_list = []
    column_filters = ['timeStamp', 'pls_wallet_payer', 'trx_pay_date', 'approved', 'paid']
    form_excluded_columns = ['pls_payable_amount']
    form_widget_args = {}
    column_labels = {
        'share_sequence' : 'Sequence',
        'timeStamp': 'Timestamp',
        'pls_wallet_payer': 'Payee Wallet',
        'pls_payable_amount': 'Payable amount',
        'trx_pay_date' : 'Payment Date',
        'trx_hash' : 'Transaction Hash'
    }
    form_overrides = {
    }
    form_extra_fields = {
        'pls_wallet_payer' : sqla.fields.QuerySelectField('Payer Wallet', query_factory=lambda: pls_wallets.get_all(), allow_blank=False, blank_text='(Select a Wallet to Generate Order)'),
        # 'task_rel' : sqla.fields.QuerySelectField('Task Name', query_factory=lambda: task_list.get_all(), allow_blank=False, blank_text='(Select a Task)'),
        # 'task_cron' : fields.StringField('Cron Schedule', validators=[validators.DataRequired()]),
        # 'task_active' : fields.BooleanField('Active?', default=False),
    }
    
    creation_attributes = ['pls_wallet_payer']
    creation_attributes_titles = ['Select Payer Wallet to Generate Order']
        
    def is_accessible(self):
        set_template_objects(self)
        return login.current_user.is_authenticated and (login.current_user.is_admin or login.current_user.is_staff)

    # Custom creation form
    def create_form(self, obj=None):
        form = super().create_form(obj=obj)
        form_attributes = self.creation_attributes
        for field in list(form):
            if field.name not in form_attributes:
                form._fields.pop(field.name)
        return form
    
    # Custom edit form
    def on_form_prefill(self, form, id):
        form_attributes = self.creation_attributes
        for field in list(form):
            if field.name in form_attributes:
                form._fields.pop(field.name)
        return form
    
    # change creation process
    def create_model(self, form):
        SHARE_PCT = myconfig['REWARD_BASE_PCT']
        pls_wallet_payer = form.data['pls_wallet_payer']
        pls_wallet_address = pls_wallet_payer.address
        pls_wallet_owner = pls_wallet_payer.owner
        pls_share_sequence = pls_share_seq.new_sequence(pls_wallet_address, rand_string(6))
        last_pls_price = pls_price.get_last()
        priceUSD, priceFX = last_pls_price.priceUSD, last_pls_price.priceFX
        
        # lets get pending transactions
        pls_pending_transactions = pls_validator_withdrawals.get_not_in_share_by_wallet(pls_wallet_address)
        
        total_registered = 0
        total_witdrawed = 0
        total_shared = 0        
        if pls_pending_transactions is not None:
            for pls_share_trx in pls_pending_transactions:
                sequence_txt = pls_share_sequence.pls_sequence
                sequence_idx = pls_share_sequence.index
                withdrawal_id = pls_share_trx.index
                validatorIndex = pls_share_trx.validatorIndex
                blockNumber = pls_share_trx.blockNumber
                timeStamp = pls_share_trx.timeStamp
                withdrawed_amount = pls_share_trx.amount
                share_amount = withdrawed_amount * SHARE_PCT
                total_witdrawed += withdrawed_amount
                total_shared += share_amount
                try:
                    pls_share_details.new_detail(sequence_idx, pls_wallet_payer.address, withdrawal_id, validatorIndex, blockNumber, timeStamp, withdrawed_amount, SHARE_PCT, share_amount)
                except Exception as e:
                    flash(f'SEQUENCE [{sequence_txt}] - Error creating share detail for {pls_wallet_payer.address} {pls_wallet_payer.owner} - {e}', 'error')
                    break
                total_registered += 1
                
            # once all transactions are done
            try:
                pls_share.new_header(sequence_idx, pls_wallet_payer, total_witdrawed, total_shared, priceUSD, priceFX)
            except Exception as e:
                flash(f'SEQUENCE [{sequence_txt}] - Error creating share header for {pls_wallet_payer.address} {pls_wallet_payer.owner} - {e}', 'error')
                
            log2store = LOG_CREATE % (login.current_user.email, form.data)
            logger.info(log2store)
            new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CREATE}', data=log2store, image=None)
            flash(f'{SHARE_PCT} for address {pls_wallet_payer.address} owned by {pls_wallet_payer.owner} had {len(pls_pending_transactions)} pending transactions.', 'warning')
            flash(f'SEQUENCE [{sequence_txt}] - {total_registered} transactions registered for {pls_wallet_payer.address} {pls_wallet_payer.owner} - {total_witdrawed} PLS withdrawn - {total_shared} PLS shared', 'success')

        else:
            flash(f'No pending transactions for {pls_wallet_payer.address} {pls_wallet_payer.owner}', 'error')
        return self.session.query(self.model)

    # disabled editing for all users except admin
    @property        
    def can_edit(self):
        return login.current_user.is_authenticated and login.current_user.is_admin

    @property        
    def can_delete(self):
        return login.current_user.is_authenticated and login.current_user.is_admin
       
    def update_model(self, form, model):
        log2store = LOG_CHANGE % (login.current_user.email, model, form.data)
        logger.info(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_INF, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_CHANGE}', data=log2store, image=None)
        return super().update_model(form, model)
    
    def delete_model(self, model):
        log2store = LOG_DELETE % (login.current_user.email, model)
        logger.warning(log2store)
        new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_DELETE}', data=log2store, image=None)
        return super().delete_model(model)
    
    # # get 
    # SHARE_PCT = myconfig['REWARD_BASE_PCT']

    # @action('create_payment', 'Create Pay Order', 'Are you sure you want to proceed?')
    # def action_create_payment(self):
    #     try:
    #         # query = self.model.query.filter(self.model.id.in_(ids)).all()
    #         # for my_record in query:            
    #         #     prev_state = 'Dismissed' if my_record.alert_dismissed else 'Active'
    #         #     my_record.alert_dismissed = not my_record.alert_dismissed
    #         #     curr_state = 'Active' if my_record.alert_dismissed else 'Dismissed'
    #         #     my_record.alert_dismissed_by = login.current_user.id
    #         #     my_record.alert_dismissed_obs = f'Alert status switched from {prev_state} to {curr_state} by {login.current_user.email}'
    #         #     db.session.commit()
    #         log2store = LOG_BATCH % (login.current_user.email, 'Update', 'Alert status switched for user')
    #         logger.warning(log2store)
    #         new_log(users_id=login.current_user.id, module=self.name, severity=SEV_WRN, description=f'{__name__} | {self.category}-{self.name}: {LOG_ACT_BATCH}', data=log2store, image=None)
    #         flash('Alert switched for record(s).', 'success')
    #     except Exception as e:
    #         if not self.handle_view_exception(e):
    #             raise
    #         flash(gettext('Failed to switch: %(error)s', error=str(e)), 'error')


# ###############################
# Admin Initialization
# ###############################

# send_log(logger, 'INFO', 'ADMIN', 'ADMIN-START')
logger.info('ADMIN-START')

myadmin = admin.Admin(app, name=app.config['ADMIN_NAME'], index_view=MyAdminIndexView(), base_template='myadmin3/my_master.html', template_mode='bootstrap' + str(app.config['ADMIN_BSVERSION']))
    
# ###############################
# Category constants
# ###############################
CAT_INDENT = ' > '
CAT_PLS = 'Pulse'
CAT_PLSP = 'Payments'
CAT_SYST = 'System'
CAT_TASK = CAT_SYST + ' - Tasks'

# ###############################
# Adding admin objects
# ###############################
myadmin.add_category(name=CAT_PLS, class_name='fas fa-money-bill')
myadmin.add_view(ModelPLSWallets(pls_wallets, db.session, name='Pulse Wallets', category=CAT_PLS, menu_icon_type='fas', menu_icon_value='fa-wallet', menu_class_name='navbar-orange'))

myadmin.add_category(name=CAT_PLSP, class_name='fas fa-money-bill-wave')
myadmin.add_view(ModelShareHeaders(pls_share, db.session, name='Pulse Shares', category=CAT_PLSP, menu_icon_type='fas', menu_icon_value='fa-share-alt', menu_class_name='navbar-orange'))
myadmin.add_view(ModelShow(pls_share_details, db.session, name='Pulse Share Details', category=CAT_PLSP, menu_icon_type='fas', menu_icon_value='fa-share-alt', menu_class_name='navbar-orange'))

myadmin.add_category(name=CAT_SYST, class_name='fa fa-cogs')
myadmin.add_view(ModelUsers(Users, db.session, name='System Users', category=CAT_SYST, menu_icon_type='fa', menu_icon_value='fa-user', menu_class_name='navbar-navy'))
myadmin.add_view(ModelConfigVars(master_config, db.session, name='Config VARS', category=CAT_SYST, menu_icon_type='fas', menu_icon_value='fa-clipboard-check', menu_class_name='navbar-navy'))
myadmin.add_view(ModelLogs(logs, db.session, name=' User Logs', category=CAT_SYST, menu_icon_type='fas', menu_icon_value='fa-clipboard-list', menu_class_name='navbar-navy'))
myadmin.add_view(ModelAlertsUser(sysalerts, db.session, endpoint='myalerts', name=' My Alerts', category=CAT_SYST, menu_icon_type='fas', menu_icon_value='fa-bell', menu_class_name='navbar-navy'))
myadmin.add_view(ModelAlertsAdmin(sysalerts, db.session, endpoint='sysalerts', name=' Users Alerts', category=CAT_SYST, menu_icon_type='fas', menu_icon_value='fa-exclamation-triangle', menu_class_name='navbar-navy'))
myadmin.add_sub_category(name=CAT_TASK, parent_name=CAT_SYST)
myadmin.add_view(ModelCroner(task_scheduler, db.session, name='Scheduler', category=CAT_TASK, menu_icon_type='fas', menu_icon_value='fa-cog', menu_class_name='navbar-navy'))
myadmin.add_view(tasks(name='Status', category=CAT_TASK, menu_icon_type='fas', menu_icon_value='fa-tasks', menu_class_name='navbar-navy'))
myadmin.add_view(RedisConsole(Redis(myconfig['REDIS_HOST']), name='Redis CLI', category=CAT_TASK))

#############################################
# EoF