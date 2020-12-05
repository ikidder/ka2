import os

class TestConfig:
    SECRET_KEY = str(os.urandom(16))
    DATABASE_URL = 'sqlite://'
    ENVIRONMENT = 'test'
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    PREFERRED_URL_SCHEME = 'https'



