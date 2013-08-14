"""A collection of methods to fetch information from the Meetup API
by Meetup ID and creates objects represented by the Snipey data Model
"""
import requests
from snipey.model import Event
import config
import logging


def fetch_event(event_id):
    """Make a call to the Meetup API to retrieve event information.

    NOTE: Since the event is being retrieved without authorization
    information, private groups are not supported.

    TODO: Implement Error handing, especially if the event is not
    found.

    """
    params = {
        'fields': 'rsvp_rules',
        'key': config.MEETUP_API_KEY,
    }

    url = "%sevent/%s" % (config.BASE_URL, event_id)
    resp = requests.get(url=url, params=params)
    data = resp.json()

    logging.info('fetched the json for an event with id: %s from url: %s'
                 % (event_id, url))

    return data
