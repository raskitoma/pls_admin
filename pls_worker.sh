#!/bin/bash
# Run Celery Beat
celery -A app.scheduler.celery beat --loglevel=info --detach --pidfile=''
# Run Celery Worker
celery -A app.scheduler.celery worker --loglevel=info -E --detach --pidfile=''
