#!/bin/bash
# Run Celery Worker
celery -A app.scheduler.celery worker --loglevel=info -E --detach --pidfile=''
# Run Celery Beat
celery -A app.scheduler.celery beat --loglevel=info --detach --pidfile=''
# Run Flask App (PPMCore)
flask run --host=0.0.0.0 --port=5000