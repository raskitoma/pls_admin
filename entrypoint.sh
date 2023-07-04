#!/bin/bash
# Run Celery Worker
python3 -m celery app.scheduler.celery worker --loglevel=info -E --detach --pidfile=''
# Run Celery Beat
python3 -m celery app.scheduler.celery beat --loglevel=info --detach --pidfile=''
# Run Flask App (PPMCore)
python3 -m flask run --host=0.0.0.0 --port=5000