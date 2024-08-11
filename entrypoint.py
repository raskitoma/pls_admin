# RSK - Core
# 2023 (c) All rights reserved
# by Raskitoma.com/Raskitoma.io
import json
import os
from werkzeug.security import generate_password_hash
from sqlalchemy import text

from app import create_app
from app.rskcore.utl import get_time, prGreen, prRed, prYellow

settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)

# setting up db
from app import db
from app.rskcore.models import *
with app.app_context():
    db.create_all()

# launching admin
with app.app_context():
    from app.rskcore import admin

# function for creating admin user
global DEFAULT_ADMIN_NAME
DEFAULT_ADMIN_NAME = 'admin@rskcore.io'

def admin_create(admin_name, admin_password):
    adminio = Users(
        created_at = datetime.now(),
        modified_at = datetime.now(),
        email = admin_name, 
        fullname = 'Admin RSK-Core',
        password = generate_password_hash(admin_password),
        active = True,
        verified = datetime.now(),
        access = {'admin': True, 'staff': True, 'customer': True},
        admin = True,
        staff = True
    )
    db.session.add(adminio)
    print ('Admin created with provided password')

# creating console commands
import click
# Admin update
@app.cli.command('update-admin')
def create_admin():
    # request input for passwords
    password = click.prompt('Enter password for admin', hide_input=True, confirmation_prompt=True)
    from app.rskcore.models import Users
    # lets check if admin exists, if not create it
    adminio = Users.query.filter_by(email=DEFAULT_ADMIN_NAME).first()
    if adminio is None:
        print ('Admin does not exist, creating it')
        admin_create(DEFAULT_ADMIN_NAME, password)
    else:
        print ('Admin exists, updating it')
        adminio.password =  generate_password_hash(password)
    db.session.commit()
    print ( 'Admin management complete!')
    
# First Run
@app.cli.command('first-run')
def init_db():
    print('System restore procedure...')
    print('Current database will be dropped and recreated from scratch')
    print('All data will be lost!')
    print('Database URI: ' + str(db.engine.url))
    lets_proceed = click.prompt('This is a destructive operation, to proceed you must type "Proceed!"', default='Abort', show_default=True)
    if lets_proceed != 'Proceed!':
        print('Database initialization aborted')
        exit()
    lets_proceed = click.confirm('Are you sure you want to initialize the database?', abort=True)
    if lets_proceed:
        db.drop_all()
        db.create_all()
        print ('Database initialized')
    else:
        print('Database initialization aborted')
        exit()
    # fils db with initial data
    schedules_data = json.load(open('scheduler/config.json'))
    for scheduler_task in schedules_data:
        new_task = task_list(
            task_name = scheduler_task['task_name'],
            task_description=scheduler_task['task_description'],
            task_type=scheduler_task['task_type']
        )
        db.session.add(new_task)    
    # lets check if admin exists, if not create it
    adminio = Users.query.filter_by(email=DEFAULT_ADMIN_NAME).first()
    if adminio is None:
        print (f'Admin does not exist, creating {DEFAULT_ADMIN_NAME} with default password...')
        admin_create(DEFAULT_ADMIN_NAME, 'admin')
    db.session.commit()    
    print('Database initialization complete!')

# Scheduler
@app.cli.command('scheduler-reset')
def scheduler_reset():
    print('Scheduler restore procedure...')
    print('Current scheduler data will be deleted and recreated from scratch')
    print('All schedule data will be lost!')
    print('Database URI: ' + str(db.engine.url))
    lets_proceed = click.prompt('This is a destructive operation, to proceed you must type "Proceed!"', default='Abort', show_default=True)
    if lets_proceed != 'Proceed!':
        print('Schedule re-initialization aborted')
        exit()
    lets_proceed = click.confirm('Are you sure you want to initialize the schedule?', abort=True)
    if lets_proceed:
        t = text("TRUNCATE TABLE task_scheduler CASCADE")
        db.session.execute(t)
        #db.session.execute('TRUNCATE TABLE task_scheduler CASCADE')
        t = text("TRUNCATE TABLE task_list CASCADE")
        db.session.execute(t)
        #db.session.execute('TRUNCATE TABLE task_list CASCADE')
        schedules_data = json.load(open('scheduler/config.json'))
        for scheduler_task in schedules_data:
            new_task = task_list(
                task_name = scheduler_task['task_name'],
                task_description=scheduler_task['task_description'],
                task_type=scheduler_task['task_type']
            )
            db.session.add(new_task)
        db.session.commit()
        print ('Scheduler reset complete!')
    else:
        print('Scheduler re-initialization aborted')
        exit()

# First-run sync
@app.cli.command('first-sync')
def firstsync():
    prGreen(f'{get_time()} | FIRST-SYNC ====================>>> First sync started')
    from app.scheduler_tasks import validator_update, wallets_review, pls_price_update
    pls_price_update()
    wallets_review()
    validator_update()

@app.cli.command('one-time-sync')
@click.argument('xfrom', default=1, nargs=1)
@click.argument('xto', default=1 , nargs=1)
def firstsync(xfrom, xto):
    prGreen(f'{get_time()} | ONE-TIME-SYNC ====================>>> First sync started')
    if xfrom is None or xto is None:
        prRed(f'{get_time()} | You must supply two parameters, first and last block to sync')
        exit()
    if xfrom < xto:
        prRed(f'{get_time()} | First parameter must be greater than second')
        exit()
    from app.scheduler_tasks import pls_custom_sync
    pls_custom_sync(xfrom, xto)
    
# if __name__ == '__main__':
#     from app.scheduler import celery
#     application = current_app._get_current_object()
#     worker = celery.Worker(app=application)
#     options = {
#         'broker': app.config['REDIS_BROKER_URL'],
#         'loglevel': 'INFO',
#         'traceback': True,
#         'beat': True
#     }
#     worker.run(**options)
    
# EoF
