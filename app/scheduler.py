#############################################
# core_scheduler_tasks.py
# (c)2023, Raskitoma.com
#--------------------------------------------
# Scheduler tasks for Core
#-------------------------------------------- 
# TODO - Add extra functionality
#-------------------------------------------- 
# from entrypoint import app
import shutil
from app import create_app
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
import os
import datetime
from app import db
from .rskcore.models import task_scheduler
from .rskcore.utl import new_log
from .scheduler_tasks import pls_price_update, wallets_review, validator_update

# setup logger
logger = get_task_logger(__name__)

# setup app operation
settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)

# Setup basic celery scheduler(scheduler will be loaded from DB)
app.config['CELERYBEAT_SCHEDULE'] = {}

## Functions for task scheduler

# Updates a task last run time
def update_task_last_run(task_name):
    runner = task_scheduler.get_task_by_name(task_name)
    my_task = celery.tasks.get(task_name)
    if runner is not None:
        runner.task_last_run = datetime.datetime.utcnow()
        runner.task_worker_id = my_task.request.id
        db.session.commit()

# Gets all tasks as an array of objects
def get_tasks(mode='active'):
    task_statuses = []
    if mode == 'active':
        task_list = task_scheduler.get_active()
    elif mode == 'disabled':
        task_list = task_scheduler.get_inactive()
    else:
        task_list = task_scheduler.get_all()
    for task in task_list:
        try:
            task_info = AsyncResult(task.task_worker_id, app=celery)
            task_info_obj = {
                "task_id": task_info.id,
                "task_name": task.task_rel.task_name,
                "task_status": task_info.status,
                "task_result": task_info.result,
                "task_state": task_info.state,
                "task_last_run": task_info.date_done.strftime("%Y-%m-%d %H:%M:%S"),                
            }
            task_statuses.append(task_info_obj)
        except Exception as e:
            print(e)
            continue
    return task_statuses

# Celery Object Creation and Configuration
def make_celery(app):
    celery = Celery(app.name, result_backend=app.config['REDIS_RESULT_BACKEND'], broker=app.config['REDIS_BROKER_URL'])
    celery.conf.update(
        result_backend=app.config['REDIS_RESULT_BACKEND'],
        broker_url=app.config['REDIS_BROKER_URL'],
        timezone="UTC",
        task_serializaer="json",
        accept_content=["json"],
        result_serializer="json",
        beat_schedule=app.config['CELERYBEAT_SCHEDULE']
    )
    taskbase = celery.Task
    class ContextTask(taskbase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return taskbase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# @celery.on_after_configure.connect
# Gets all enabled tasks an load them into Celery
def setup_periodic_tasks(sender, **kwargs):    
    active_tasks=task_scheduler.get_active()
    loaded_tasks = {}
    for task in active_tasks:
        task_name = task.task_rel.task_name
        cron_schedule = task.task_cron.split()
        cron_args = crontab(minute=cron_schedule[0], hour=cron_schedule[1], day_of_week=cron_schedule[2], day_of_month=cron_schedule[3], month_of_year=cron_schedule[4])
        task_object = {
            "task": task_name,
            "schedule": cron_args,
        }
        loaded_tasks[task_name] = task_object       
    # update celery beat schedule and config
    sender.conf.update(
        beat_schedule=loaded_tasks
    )

# PLS Price update
@celery.task(name='pls_pu', bind=True, rate_limit='1/m')
def pls_pu(self):
    # clean uploads folder
    logger.info('PLS Price Update - Started')
    with_errors = ''
    try:
        pls_price_update()
    except Exception as e:
        logger.error('Failed PLS price update from API. Reason: %s' % (e))
        with_errors = ' - With errors, check logs'
    update_task_last_run('pls_pu')
    logger.info(f'PLS Price Update Done{with_errors}')

# Wallets Review
@celery.task(name='pls_wr', bind=True, rate_limit='1/m')
def pls_wr(self):
    # clean uploads folder
    logger.info('PLS Wallets Review - Started')
    with_errors = ''
    try:
        wallets_review()
    except Exception as e:
        logger.error('Failed Wallets Review. Reason: %s' % (e))
        with_errors = ' - With errors, check logs'
    update_task_last_run('pls_wr')
    logger.info(f'PLS Wallets Review Done{with_errors}')

# Validators Update
@celery.task(name='pls_vu', bind=True, rate_limit='1/m')
def pls_vu(self):
    # clean uploads folder
    logger.info('PLS Validators Update - Started')
    with_errors = ''
    try:
        validator_update()
    except Exception as e:
        logger.error('Failed Validator Update. Reason: %s' % (e))
        with_errors = ' - With errors, check logs'
    update_task_last_run('pls_vu')
    logger.info(f'PLS Validators Update Done{with_errors}')
   
with app.app_context():
    setup_periodic_tasks(celery)

if __name__ == '__main__':
    celery.start()