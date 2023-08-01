# Dockerfile
FROM python:3.8-slim-buster
LABEL MAINTAINER="Raskitoma.com/EAJ"
LABEL VERSION="1.0"
LABEL LICENSE="GPLv3"
LABEL DESCRIPTION="Raskitoma-RskCore"

# installing locales
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

# setting env vars
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV TZ=America/New_York
ENV FLASK_APP=entrypoint
ENV APP_SETTINGS_MODULE=config.dev

# create required folders
RUN mkdir -p /app/db
RUN mkdir -p /app/media
RUN mkdir -p /app/media/uploads
RUN mkdir -p /app/app
RUN mkdir -p /app/config
RUN mkdir -p /app/app/rskcore
RUN mkdir -p /app/app/templates
RUN mkdir -p /app/scheduler

# setting workdir
WORKDIR /app

# copy requirements file
COPY requirements.txt /app/requirements.txt
# installing needed python libraries
RUN pip3 install -r requirements.txt

# copying required files
COPY entrypoint.sh /app/
COPY *.py /app/
COPY app /app/app
COPY config /app/config
COPY scheduler /app/scheduler

# setting permissions to entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exposing main port
EXPOSE 5000

# Startup
CMD ["./entrypoint.sh"]
# CMD ["sh", "-c", "python3 -m flask run --host 0.0.0.0 --port 5000 & celery -A app.scheduler.celery worker --loglevel=INFO --detach --pidfile='' & celery -A app.scheduler.celery beat --loglevel=INFO --detach --pidfile=''"]