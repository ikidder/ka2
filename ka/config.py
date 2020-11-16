import os
from dotenv import load_dotenv

if os.environ.get('ENVIRONMENT') == 'development':
    load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    # ELASTICSEARCH_URL = os.environ.get('FOUNDELASTICSEARCH_URL')
    # ELASTICSEARCH_CLOUD_ID = os.environ.get('ELASTICSEARCH_CLOUD_ID')
    # ELASTICSEARCH_USER_NAME = os.environ.get('ELASTICSEARCH_USER_NAME')
    # ELASTICSEARCH_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD')
    # ELASTICSEARCH_ENVIRONMENT_PREFIX = os.environ.get('ELASTICSEARCH_ENVIRONMENT_PREFIX')

