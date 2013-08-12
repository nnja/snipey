import logging
from snipey import tasks
from snipey import db
from snipey.model import Event, Group, Snipe, Stream
import requests
import simplejson as json
from datetime import datetime
import config

EVENT_STREAM_URL = 'http://stream.meetup.com/2/open_events'


def connect(since_time):
    """ Connect to the stream API, retrieving data from the provided
    since_time.

    """
    logging.info('connect to meetup rsvp. since_time: %s' % since_time)
    process_stream(open_event_stream(since_time=since_time))


def open_event_stream(url=EVENT_STREAM_URL, since_time=None):
    """ Open a stream to the Meetup Open Events API

    Documentation located at:
    http://www.meetup.com/meetup_api/docs/stream/2/open_events/

    An optional since_time can be passed in to back process events
    that occured after a certain time.

    """
    logging.info('open_event_stream. url:%s, since_time: %s'
                 % (url, since_time))

    params = {}
    if since_time is not None:
        params['since_mtime'] = since_time

    return requests.get(url, params=params, stream=True)


def process_stream(request):
    """ Process the incoming request stream.

    If the connection is lost, proceed to reconnect, providing
    the mtime of lost connection.

    TODO: This whole unit of work should be done as a celery task.

    """
    logging.info('processing stream.')

    for line in request.iter_lines():
        data = json.loads(line)

        meetup_group_id = data['group']['id']
        event_url = data['event_url']

        logging.info('meetup_group_id: %s, event_url: %s mtime: %s'
                     % (meetup_group_id, event_url, data['mtime']))

        parse_snipes(meetup_group_id, event_url)

        track_mtime(data['mtime'])


def track_mtime(mtime):
    """ Keep track of the last event's mtime, which can be used to
    resume a dropped connection.

    """
    stream = Stream.current()
    stream.since_mtime_milli = mtime
    db.session.commit()


def parse_snipes(meetup_group_id, event_url):
    """ If a matching subscription exists in the system for the meetup
    group_id, create the event and process snipes for all users.

    """

    group = Group.query.filter(Group.meetup_id == meetup_group_id).first()

    if group and group.subscribers:
        event_id = get_event_id(event_url)
        event = create_event(group, event_id)
        create_snipes(event)


def get_event_id(event_url):
    """ Parse the event_id from the event_url.

    The event_url is in the format:
    http://www.meetup.com/<group_name>/events/<event_id>/

    The event id may be numeric or alphanumeric.
    """

    return event_url.split('/')[-2]


def create_snipes(event):
    """ Given a group id and an event, create snipes for all subscribers.

    Dispatch celery tasks for every snipe. If the event has an
    rsvp_open time, dispatch the task with an eta.

    """
    logging.info('creating snipes')
    for user in event.group.subscribers:
        snipe = Snipe(event_id=event.id, user_id=user.id)
        db.session.add(snipe)
        db.session.commit()

        logging.info('created snipe with id: %s' % snipe.id)
        if snipe.event.rsvp_open_time:
            logging.info('scheduling celery task for snipe.id %s and eta %s'
                         % (snipe.id, snipe.event.rsvp_open_time))
            tasks.rsvp.delay(snipe.id,
                             event.meetup_id,
                             user.token,
                             eta=snipe.event.rsvp_open_time)
        else:
            logging.info('scheduling celery task for snipe.id %s immediately'
                         % snipe.id)
            tasks.rsvp.delay(snipe.id, event.meetup_id, user.token)


def create_event(group, event_id):
    """ Make a call to the Meetup API to retrieve event information.

    Use the data to create a reference event in the database.

    NOTE: Since the event is being retrieved without authorization
    information, private groups are not supported.

    TODO: Implement Error handing, especially if the event is not found.
    """

    params = {
        'fields': 'rsvp_rules',
        'key': config.MEETUP_API_KEY,
    }

    url = "%sevent/%s" % (config.BASE_URL, event_id)
    resp = requests.get(url=url, params=params)
    data = resp.json()

    logging.info('creating an event for group %s and event_id: %s and url:%s'
                 % (group.id, event_id, url))
    logging.info('data is: %s' % data)

    name = data['name']
    open_time = data['rsvp_rules'].get('open_time')
    if open_time:
        open_time = datetime.utcfromtimestamp(open_time//1000).replace(
            microsecond=open_time % 1000*1000)

    event = Event(group=group,
                  meetup_id=event_id,
                  name=name,
                  rsvp_open_time=open_time)

    db.session.add(event)
    db.session.commit()

    logging.info('created event with id: %s' % event.id)

    return event
