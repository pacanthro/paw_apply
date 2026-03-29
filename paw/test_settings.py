# myproject/test_settings.py
from .settings import *  # Import standard settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', # Use ':memory:' for an in-memory database
    }
}