import logging
from snipey import db, tasks, meetup
from snipey.model import Group, Snipe, Stream, Event
import requests
import simplejson as json

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

    TODO: Event with a status of cancled should not be scheduled for snipe.

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
        event = get_event(event_id)
        event.url = event_url
        create_snipes(event)


def get_event(event_id):
    """Get an event by a meetup event_id.

    If the event exists in the database, return it. Otherwise create
    an event from data provided by the Meetup API.

    """
    event = Event.query.filter_by(meetup_id=event_id).first()
    if event:
        return event

    data = meetup.fetch_event(event_id)

    event = Event.from_json(data)
    db.session.add(event)
    db.session.commit()

    logging.info('created event with id: %s' % event.id)
    return event


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
            tasks.rsvp.apply_async(args=[snipe.id,
                                         event.meetup_id,
                                         user.token],
                                   eta=snipe.event.rsvp_open_time)
        else:
            logging.info('scheduling celery task for snipe.id %s immediately'
                         % snipe.id)
            tasks.rsvp.delay(snipe.id, event.meetup_id, user.token)
