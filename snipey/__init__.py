from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.oauth import OAuth
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

Bootstrap(app)

oauth = OAuth()
meetup_oauth = oauth.remote_app('meetup',
                          base_url='https://api.meetup.com/2/',
                          request_token_url='https://api.meetup.com/oauth/request',
                          access_token_url='https://api.meetup.com/oauth/access',
                          authorize_url='http://www.meetup.com/authorize',
                          consumer_key=app.config['CONSUMER_KEY'],
                          consumer_secret=app.config['CONSUMER_SECRET'])

from snipey import view
