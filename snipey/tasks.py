from snipey import celery, db
from snipey.model import User, Snipe
from flask.globals import current_app
import config
from flask_oauth import OAuth


celery_oauth = OAuth().remote_app('meetup',
                                  base_url=config.BASE_URL,
                                  request_token_url=config.REQUEST_TOKEN_URL,
                                  access_token_url=config.ACCESS_TOKEN_URL,
                                  authorize_url=config.AUTHORIZE_URL,
                                  consumer_key=config.CONSUMER_KEY,
                                  consumer_secret=config.CONSUMER_SECRET)


@celery_oauth.tokengetter
def celery_token_getter(token=None):
    current_app.logger.info('attempting to fetch user for token: %s' % token)

    if token:
        user = User.query.filter_by(token=token).first()

        if user:
            return user.token, user.secret
        else:
            current_app.logger.error('no user found for token: %s' % token)
    else:
        current_app.logger.error(
            'no token provided to celery_oauth tokengetter')

    return None, None


@celery.task()
def rsvp(snipe_id, meetup_event_id, token):
    """Attempt to RSVP to an event with the given credentials.

    Update the snipe status in the database once complete.

    """
    current_app.logger.info(
        'attempting to rsvp snipe.id: %s for event_id:%s, token: %s'
        % (snipe_id, meetup_event_id, token))

    snipe = Snipe.query.filter(Snipe.id == snipe_id).first()
    if not snipe:
        current_app.logger.error('Snipe with id: %s not found!' % snipe_id)
        return
    elif snipe.status == Snipe.CANCELED:
        current_app.logger.info('Snipe with id: %s was canceled.' % snipe_id)
        return

    resp = celery_oauth.post('rsvp', token=token, data={
        'event_id': meetup_event_id,
        'rsvp': 'yes'
    })

    if resp.status == 201:
        current_app.logger.info('rsvping snipe_id: %s OK!' % snipe.id)
        snipe.status = Snipe.SUCCEEDED
    else:
        current_app.logger.error('rsvping snipe_id: %s FAILED.' % snipe.id)
        snipe.status = Snipe.FAILED
        if 'details' in resp:
            snipe.error_msg = resp['details']

    db.session.commit()
