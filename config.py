import os

DEBUG = os.getenv('DEBUG', True)

BASEDIR = os.path.abspath(os.path.dirname(__file__))

## Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///%s' %
                                    os.path.join(BASEDIR, 'app.db'))

BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_USE_CDN = FalseBOOTSTRAP_FONTAWESOME = True

SECRET_KEY = os.getenv('SECRET_KEY', 'devkey')

# Meetup Specific Settings
MEETUP_URL = 'http://www.meetup.com/'
BASE_URL = 'https://api.meetup.com/2/'
REQUEST_TOKEN_URL = 'https://api.meetup.com/oauth/request'
ACCESS_TOKEN_URL = 'https://api.meetup.com/oauth/access'
AUTHORIZE_URL = '%sauthorize' % MEETUP_URL
CONSUMER_KEY = os.getenv('CONSUMER_KEY', 'your consumer key')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', 'your consumer secret')
MEETUP_API_KEY = os.getenv('MEETUP_API_KEY', 'your meetup api key')

# Celery Settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL',
                              'amqp://guest:guest@localhost:5672//')
