import os
import config

from flask import Flask
from celery import Celery
from flask_oauth import OAuth
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)
Bootstrap(app)

oauth = OAuth()
meetup_oauth = oauth.remote_app('meetup',
                                base_url=config.BASE_URL,
                                request_token_url=config.REQUEST_TOKEN_URL,
                                access_token_url=config.ACCESS_TOKEN_URL,
                                authorize_url=config.AUTHORIZE_URL,
                                consumer_key=config.CONSUMER_KEY,
                                consumer_secret=config.CONSUMER_SECRET)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

from snipey import view
