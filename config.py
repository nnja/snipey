import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///%s' %
                                    os.path.join(BASEDIR, 'app.db'))

BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_USE_CDN = False
BOOTSTRAP_FONTAWESOME = True

SECRET_KEY = os.getenv('SECRET_KEY', 'devkey')

# Meetup Specific Settings
BASE_URL = 'https://api.meetup.com/2/'
REQUEST_TOKEN_URL = 'https://api.meetup.com/oauth/request'
ACCESS_TOKEN_URL = 'https://api.meetup.com/oauth/access'
AUTHORIZE_URL = 'http://www.meetup.com/authorize'
CONSUMER_KEY = os.getenv('CONSUMER_KEY', 'your consumer key')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', 'your consumer secret')
