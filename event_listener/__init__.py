from snipey.model import Event
import requests
import simplejson as json
from datetime import datetime

EVENT_STREAM_URL = 'http://stream.meetup.com/2/open_events'


def open_event_stream(url=EVENT_STREAM_URL, since_time=''):
    """Open a stream to the Meetup Open Events API

    http://www.meetup.com/meetup_api/docs/stream/2/open_events/

    An optional since_time can be passed in to back process events
    that occured after a certain time.
    """

    return requests.get(url, stream=True)


def reconnect(since_time=datetime.now()):
    process_stream(open_event_stream(since_time=since_time))


def process_stream(request):
    """
    Process the incoming request stream.

    If the connection is lost, proceed to reconnect, providing
    the mtime of lost connection.
    """

    for line in request.iter_lines():
        process_json(json.loads(line))
    else:
        reconnect()


def process_json(json):
    """
    Process the incoming JSON. If a matching subscription exists in
    the system for the meetup group_id, create a snipe.
    """

    group_id = json['group']['id']

    if subscription_exists(group_id):
        event_id = get_event_id(json[['event_url']])
        event = create_event(event_id)
        create_snipes(group_id, event)


def subscription_exists(group_id):
    """
    Check to see if a subscription exists for a given group id.
    """

    pass


def create_snipes(group_id, event):
    """
    Given a group id and an event, create snipes for all subscribers.

    Dispatch celery tasks for every snipe. If the event has an
    rsvp_open time, dispatch the task with an eta.
    """

    pass


def get_event_id(event_url):
    """Parse the event_id from the event_url.

    The event_url is in the format:
    http://www.meetup.com/<group_name>/events/<event_id>

    TODO: This is terrible. Take the time to re-implement this with
    regular expressions
    """

    return event_url.split('/')[-2]


def create_event(event_id):
    # Make an API call to the meetup api, get the event json
    json = {}

    meetup_id = event_id
    group_id = json['group']['id']
    name = json['name']

    if json['rsvp_rules']:
        open_time = json['rsvp_rules']['open_time']

    return Event(group_id=group_id,
                 meetup_id=meetup_id,
                 name=name,
                 rsvp_open_time=open_time)
