# Settings file
# Raskitoma.io
from os.path import abspath, dirname, join

# Define the application directory
BASE_DIR = dirname(dirname(abspath(__file__)))

# Media dir
MEDIA_DIR = join(BASE_DIR, 'media')
UPLOADS_DIR = join(MEDIA_DIR, 'uploads')
DB_DIR = join(BASE_DIR, 'db')
DB_DEV = join(DB_DIR, 'rskcore.db')

SECRET_KEY = '1234567890abcdefg1234567890abcdefg1234567890abcdefg1234567890abcdefg1234567890abcdefg'

# Defining allowed extensions
allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'tif', 'pdf'}

# Disable Customer Portal
ADMIN_ONLY = True

# Database configuration
SQLALCHEMY_TRACK_MODIFICATIONS = False

# App environments
APP_ENV_LOCAL = 'local'
APP_ENV_TESTING = 'testing'
APP_ENV_DEVELOPMENT = 'development'
APP_ENV_STAGING = 'staging'
APP_ENV_PRODUCTION = 'production'
APP_ENV = ''

# TIME ZONE
APP_TIMEZONE = 'America/New_York'

# Template layout settings
ADMIN_SKIN = 'pulse'
ADMIN_NAME = 'Pulse Manager - RskCore.io'
ADMIN_DESC = 'Admin Console'
ADMIN_GRAFANA_URL = 'https://mygrafana.com'
ADMIN_LOGO = 'https://raskitoma.com/assets/media/rask-favicon.svg'
ADMIN_FAVICON = 'https://raskitoma.com/favicon.ico'
ADMIN_FOOTER = '&copy; 2023, <a class="text-dark" href="https://raskitoma.com">Raskitoma.com</a>'
ADMIN_MODAL = False # Disabling modal for windows
ADMIN_BSVERSION = 4
FLASK_ADMIN_FLUID_LAYOUT = True
ITEMS_PER_PAGE = 50
# https://adminlte-full.readthedocs.io/en/latest/configuration.html#configuration
FLASK_ADMINLTE_BACK_TO_TOP = True
FLASK_ADMINLTE_LAYOUT_OPTIONS = [
        "control-sidebar-slide-open",
        "sidebar-mini",
        "text-sm",
        "layout-fixed", 
        # "sidebar-collapse",
        "layout-navbar-fixed",
        "layout-footer-fixed",
        "nav-child-indent",
    ]
FLASK_ADMINLTE_NAVBAR_OPTIONS = [
        "main-header",
        "navbar",
        "navbar-expand",
        "pb-1",
        "bg-light"
    ]

# Mail Admin settings
MAIL_SERVER = 'mymail.org'
MAIL_PORT = 587
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = 'accont@mymail.org'
MAIL_ADMIN = 'me@gmail.com'
DONT_REPLY_FROM_EMAIL = 'address from'
ADMINS = ('me@gmail.com', )
MAIL_USERNAME = 'account@mymail.org'
MAIL_PASSWORD = 'my_super_secure_app_password'
MAIL_DEBUG = False

# Syslog, Telegraf and other session variables
OTP_EXPIRE = 2
SESSION_TIMEOUT = 60
SESSION_EXP = 1440
SYSLOG_URI = 'graylog.domain.com'
SYSLOG_PORT = 514
INFLUX_HOST = 'https://influx.domain.com'
INFLUX_ORG = 'my_org'
INFLUX_BUCKET = 'dev-test'
INFLUX_TOKEN = 'aoidsufyaosdfiuyaosdifuyasdnfb921ljblasjdkfalsdf.iaosdfpoiasdfapotyasdf=='

###### Report defaults

DEFAULT_REPORT_NAME = "rskcore.pdf"

DEFAULT_REPORT_TEMPLATE = """
Hi {user}, 

This is a demo report from {app_name}.

{details}

[[PAGEBREAK]]
Please sign this form and fill the empty spaces with the requested data:

Signature:____________
Fullname:_____________
Date of signature:_____________
[[PAGEBREAK]]
This are examples for Lists:

Dashed list:
[[LIST_DASH]]
- Item 1
- Item 2
- item 3

Bullet list
[[LIST_BULLET]]
* Bullet 1
* Bullet 2
* Bullet 3

Numbered List
[[LIST_NUMBER][,]]
# First
# Second
# Third

Letter List
[[LIST_LETTER][)]]
$ Item a
$ Item b
$ Item c

"""

DEFAULT_REPORT_DATA = {
    'user' : 'Rskcore User',
    'app_name' : 'Rsk-Core',
    'details' : 'This is a sample line of details'
}

# PLS Stuff
CHAIN_URI="https://scan.pulsechain.com/api"
REWARD_BASE_PCT = 0.1
PLS_PRICE_URI="https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id=11145"
PLS_PRICE_API_KEY="jajajajajaja-jajajajajaja-jajajajajaja"
WEB3_PROVIDER_URI="https://rpc.pulsechain.com"
MAX_HEIGHT_CHECK = 17530000
PLS_PRICE_FX = 'USD'

# base broker config
REDIS_HOST = 'redis'
REDIS_BROKER_URL = f'redis://{REDIS_HOST}:6379'
REDIS_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379'

# celery config
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = APP_TIMEZONE
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


##################
# EoF