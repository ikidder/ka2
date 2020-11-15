from flask import Flask, logging
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import os

# Talisman
# for forcing https
# https://github.com/GoogleCloudPlatform/flask-talisman
# content security policy examples: https://github.com/GoogleCloudPlatform/flask-talisman#content-security-policy
from flask_talisman import Talisman

# Markdown
# flask extension: https://pythonhosted.org/Flask-Markdown/
# python module: https://python-markdown.github.io/
# syntax: https://daringfireball.net/projects/markdown/syntax
from flaskext.markdown import Markdown

# Elasticsearch
# https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html
# from elasticsearch import Elasticsearch

from .config import Config
#from .database import Session


engine = create_engine(os.environ['DATABASE_URL'], echo=True)
Session = scoped_session(sessionmaker(bind=engine))


bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    Markdown(app)

    # if app.config['ELASTICSEARCH_CLOUD_ID']:
    #     # prod
    #     app.elasticsearch = Elasticsearch(
    #         cloud_id=app.config['ELASTICSEARCH_CLOUD_ID'],
    #         http_auth=(app.config['ELASTICSEARCH_USER_NAME'], app.config['ELASTICSEARCH_PASSWORD']),
    #     )
    # else:
    #     # dev
    #     app.elasticsearch = Elasticsearch()

    from ka.users.routes import users_app
    from ka.posts.routes import posts_app
    from ka.scores.routes import scores_app
    from ka.main.routes import main_app
    from ka.errors.handlers import errors_app
    from ka.search.routes import search_app
    app.register_blueprint(users_app)
    app.register_blueprint(posts_app)
    app.register_blueprint(scores_app)
    app.register_blueprint(main_app)
    app.register_blueprint(errors_app)
    app.register_blueprint(search_app)

    sec_policy = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '\'unsafe-eval\'',
            'stackpath.bootstrapcdn.com',
            'code.jquery.com',
            'cdn.jsdelivr.net',
            'use.fontawesome.com',
            'fonts.googleapis.com',
            'fonts.gstatic.com'
        ]
    }
    Talisman(app,
             content_security_policy=sec_policy)

    @app.teardown_appcontext
    def cleanup(resp_or_exc):
        Session.remove()

    return app


