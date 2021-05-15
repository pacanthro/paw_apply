# Deploy Instructions

## Git
1. `sudo git pull`

## Activate VENV
1. `source venv/bin/activate`
1. `source .env`
1. `pip3 install -r requirements.txt`

## Django Stuff
1. `python3 manage.py collectstatic`
1. `python3 manage.py makemigrations`
1. `python3. manage.py migrate`
