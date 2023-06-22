# RSK - Core
# 2023 (c) All rights reserved
# by Raskitoma.com/Raskitoma.io

from .default import *

APP_ENV = APP_ENV_DEVELOPMENT

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_DEV)

ADMIN_ONLY = True

# EoF
