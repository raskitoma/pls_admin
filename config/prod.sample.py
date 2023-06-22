# RSK - Core
# 2023 (c) All rights reserved
# by Raskitoma.com/Raskitoma.io

from .default import *

SECRET_KEY = '5e04a4955d8878191923e86fe6a0dfb24edb226c87d6c7787f35ba4698afc86e95cae409aebd47f7'

APP_ENV = APP_ENV_PRODUCTION

FLASK_ADMINLTE_LAYOUT_OPTIONS = [
        "control-sidebar-slide-open",
        "sidebar-mini",
        "text-sm",
        "layout-fixed", 
        "sidebar-collapse",
        "layout-navbar-fixed",
        "layout-footer-fixed",
    ]

# PUT OTHER VARS HERE REFER TO default.py FOR EXAMPLES


# Values for PLS Grabber
CHAIN_URI="https://scan.pulsechain.com/api"
SQLALCHEMY_DATABASE_URI = 'postgresql://db_user:db_pass@host:port/db_name'
PLS_PRICE_URI="https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id=11145"
PLS_PRICE_API_KEY="my-coinmarketcap-api-key"
WEB3_PROVIDER_URI="https://rpc.pulsechain.com"
ADMIN_GRAFANA_URL = 'https://mygrafana.com'
MAX_HEIGHT_CHECK = 17530000 # use a reasonable height... first sync will take a while

# EoF
