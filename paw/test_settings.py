# myproject/test_settings.py
from .settings import *  # Import standard settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR + '/db_tests.sqlite3', # Use ':memory:' for an in-memory database
    }
}