# PAWApply
PAWApply is a Django based website for Furry Conventions to facilitate helping Attendees apply for:

* Dealers Den (Shopping District/Merchants)
* Volunteering
* Party Floor
* Panels
* Dance Comp

With the exception of Volunteers all of these can be toggled on and off per event.

Additionaly it's designed to automate handling of each of them. With a robust management console its very easy to approve an application,
or request a payment. A lot of steps have automated emails sent as well.

This was originally designed for Pacific Anthropomorphics Weekend ([PAWCon](https://pacanthro.org))

If you are instered in using and contributing please contact Laveur

Please Don't Open Issues or Pull Requests unless you've contacted Laveur already.

## Developer Setup
* Fork this repo and clone your fork to your local machine.
* Create a copy of `env-template` and name it `.env`
* Open the new `.env` file and change set values for the following:
    * `DJANGO_SECRET_KEY`
    * `DB_USER`
    * `DB_PASSWORD`
* Create Virtual Env using the command: `python -m venv .venv`
* Activate your Virtual Env: `source .venv/bin/activate`
* Source your environment file: `source .env`
* Install the required python modules:
    * MySQL: `pip3 install -r requirements_mysql.txt`
    * Postgres: `pip3 install -r requirements_postgres.txt`
* Create a database:
    * MySQL
        * Connect to your database `mysql -u <username> -P`
        * Create a database by running the following command: `CREATE DATABASE paw_apply;`
    * Postgres:
        * Connect to your database: `psql -U <username>`
        * Create a database by running the following command: `CREATE DATABASE paw_apply OWNER <DB_USER>;`
* Run Django check: `./manage.py check`


## Running locally
* Activate your virtual environment: `source .venv/bin/activate`
* Source your environment variables: `source .env`
* Run the dev server: `./manage.py runserver`
