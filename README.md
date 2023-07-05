# RSK - Core for PLS Admin

RSK Core is a core app to control multiple stuff. Includes default web app and admin control panel for administrative tasks.  This version is designed in mind to take care of PLS Admin tasks.

## Prerequisites

- Suggested: A Linux server (Ubuntu 20.04 LTS is recommended)
- A bit of Linux knowledge
- Docker fully configured
- Docker Compose as application or Docker plugin. (This document assumes you have Compose as plugin)
- User with privileges to run Docker commands
- Docker network strategy defined, it could be host, macvlan or bridge. (This document assumes you have a bridge network strategy)
- A DB instance, Postgres is recommended. (The app and dashboard were designed and tested with Postgres)
- A Redis instance.  The example assumes you don't have one so it will setup for you as well.

## Install

In config folder, copy `prod.sample.py` as `prod.py` and set `SQLALCHEMY_DATABASE_URI` and `SECRET_KEY` values.

Also set the following variables:

### Values for PLS Grabber

- **APP_TIMEZONE**: This is to set the time zone for the application widely, default is `America/New_York`.
- **CHAIN_URI**: `https://scan.pulsechain.com/api` is the default.
- **PLS_PRICE_URI**: This is the API from CoinMarketCap.  You need to setup an account and get a token.  Default: `https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id=11145`
- **PLS_PRICE_API_KEY**: is the token mentioned above
- **WEB3_PROVIDER_URI**: Default is `https://rpc.pulsechain.com`.
- **ADMIN_GRAFANA_URL**: This is the URL for your grafana installation. This is designed solely to have a button on the Admin's dashboard to redirect to your site.
- **MAX_HEIGHT_CHECK**: This is designed for the first time sync.  It's to prevent the sync operation to look too far up to the moment of the creation of the chain (block #0).  Default is 17530000, but you can set it to your first block height where you had your first PLS transaction.
- **REDIS_HOST**: This is the host for our Redis instance, default is `redis`.
- **REDIS_BROKER_URL**: This is used by Celery, default is `redis://{REDIS_HOST}:6379`.
- **REDIS_RESULT_BACKEND**: This is used by Celery. It can be the same as the Broker, default is `redis://{REDIS_HOST}:6379`.
- **CELERY_TASK_RESULT_EXPIRES**: Timeout for Celery tasks, default `30`.
- **CELERY_TIMEZONE**: This is the timezone for the scheduler, default is the same as the App or `APP_TIMEZONE`.

Also set a correct `docker-compose.yml` file, you can use(copy) `docker-compose.sample.yml`.  Set `TZ` to your current server's timezone, `APP_SETTINGS_MODULE` as `config.prod`.

### Network configuration

There's a special section inside the sample docker-compose file to configure the network. You can set this at the end of the compose file as follows:

```yaml
networks:
  master_network:
    external: True
```

> This network must be configured previously with the proper subnet and gateway. Assuming you are using a bridge network, you can do it with `docker network create -d bridge master_network`. More details [here](https://docs.docker.com/engine/reference/commandline/network_create/)

Once you have a network created and the network declaration inside the compose file, you need to setup the network inside each container definition as follows:

```yaml
version: "3"
services:
  container:
    image: image/name
    restart: always
    networks:           # This is the network configuration
      - master_network  # Name is the same as the one you set at the end
      # - Other_network
      # - A_macvlan_network:
      #     ipv4_address: 192.168.0.100
    environment:
      - ENV_VAR1=VALUE1
    ports:
      - 80:80

  redis:    # this is optional, you can use an external redis instance, just be sure to set the correct variables on the config as mentioned above.
    image: redis:latest
    container_name: redis
    hostname: redis
    restart: always
    ports:
      - 6379:6379
    networks:  # or the same network as the other containers
      - master_network

# ...
# Other containers, volume configurations, etc
# ...

networks:  # The network declaration as described above.
  master_network:
    external: True
```

> Note that this is a sample and it's assuming you're using a bridged network. There are diverse network configurations. The important thing is that you must set the network mode just to allow intercommunication between all containers, your DB instance and other services as well.

## Grafana Dashboard

There's a Grafana dashboard, you can import it from the extras folder. It's designed to work with the PLS grabber, so you need to setup the datasource and the variables as well.

You can find it [here](/extras/validator_performance.json).

## Usage

Assuming you have a proper *Docker* and *Docker Compose* installation, and your user has privileges to run them, you can start the application with:

```bash
    docker compose up
```

Once up, you need to run some commands to initialize the database, admin user, scheduler and other stuff.

### First run

It's not the same as `first-sync`. This is to initialize the database and create the admin user.

Once up, initialize the database with:

```bash
docker exec -it adminpls python3 -m flask first-run
docker exec -it adminpls python3 -m flask db init
```

> It will ask you to input **Proceed!** to continue and **y** to confirm. It also will create the admin user(`admin@rskcore.io`) with default password **admin**. This also will populate the tasks definition table with the default tasks so you can be able to setup the scheduler.

**About the Scheduler**

>If the scheduler doesn't shows any tasks to be configured it's because the task initialization was skipped. You can solve this by running `docker exec -it adminpls python3 -m flask scheduler-reset`. Remember that this will delete any configured schedules.

### Scheduler Config

Once you have the first run done, you must setup your schedules as follows:

1. Enter the application and go to `System > Scheduler`. Once ther, click on `Create`. You will see the following form:

![Task Creation Example](/extras/task_creation_example.png)

2. You need to select a Task(currently 3 available) from the list, set a cron (Go to [crontab.guru](https://crontab.guru/) for help) and set the `Active` checkbox if you want that schedule to be active. Suggested Cron examples for the 3 tasks above:

```cron
*/10 * * * *  # This is for the Price Update task, it will run every 10 minutes.
*/15 * * * *  # This is for the Wallet Review task, it will run every 15 minutes.
15,45 * * * *  # This is for the Validator Update task, it will run every hour at minutes 15 and 45.
```

3. Once you're done, click on `Save` and you will see the task in the list as follows:

![Task Created Example](/extras/task_created_example.png)

> By default, the form will show the `Active` checkbox as unchecked. This is to allow you to create the task and then activate it later.

**Available Tasks**

Right now there are only 3 tasks avaliable: pls_pu(Price Update, suggestion: each 10 minutes), pls_wr(Wallet Review, updates wallets balances, suggestion: each 15 minutes) and pls_vu(Validator Updates, updates validators info, suggestion: every hour at minutes 15 and 45)

> IMPORTANT: Rembember to restart the containers each time you edit a task. I will change this on the future.

### First sync

Just for the first time, you need to run the first sync. Do it with:

```bash
docker exec -it adminpls python3 -m flask first-sync
```

Once you're done with the first sync operation, you have to enable all the tasks in the scheduler to keep the sync up to date.

## Extra config and troubleshooting

### Update admin user

If you forgot your admin password, just run:

```bash
docker exec -it ppmcore adminpls -m flask update-admin
```

> Follow the prompts and confirmation for new password.

Next, if on defaults, you can access the web app at:

```bash
http://server:5000/admin
```

### Scheduler reset

If for some reason you need to reset the scheduler, you can do it with:

```bash
docker exec -it adminpls python3 -m flask scheduler-reset
```

> Take note that this will delete any configured schedules.
> This is also useful if you need to add new functions in the future.

## Upgrade

For core upgrades, you can run:

```bash
./restart_core.sh
```

> This is viable assuming you had the project already cloned with git and correct permissions.
> The script will pull the latest changes, build the new image and restart the container.
> It could be also necessary to update the DB Model.

### DB Model changes

Every other update could require model changes. If you have not initialized the database, run the following command `docker exec -it ppmcore python3 -m flask db init`, otherwise run:

```bash
docker exec -it adminpls python3 -m flask db migrate
```

Once you review the changes, run:

```bash
docker exec -it adminpls python3 -m flask db upgrade
```

Check any error output for possible issue tracking.

## Code quality status

> wip - raskitoma.io
