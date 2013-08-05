from flask import Flask
from flask_oauth import OAuth
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import config


app = Flask(__name__)
app.config.from_object('config')

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

from snipey import view
