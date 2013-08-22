"""A collection of methods to fetch information from the Meetup API
by Meetup ID and creates objects represented by the Snipey data Model
"""
import requests
import config
import logging


def fetch_event(meetup_id):
    """ Make a call to the Meetup API to retrieve event information.

    NOTE: Since the event is being retrieved without authorization
    information, private groups are not supported.

    TODO: Implement Error handing, especially if the event is not
    found.

    """
    params = {
        'fields': 'rsvp_rules',
        'key': config.MEETUP_API_KEY,
    }

    url = '%sevent/%s' % (config.BASE_URL, meetup_id)
    resp = requests.get(url=url, params=params)
    data = resp.json()

    logging.info('fetched the json for an event meetup_id: %s from url: %s'
                 % (meetup_id, url))

    return data


def fetch_groups(meetup_ids):
    """ Make a call to the MeetupAPI to retrieve group information.

    The api will return a list of results, even if only one ID is passed in.
    """
    ids = ','.join(map(str, meetup_ids))

    params = {
        'key': config.MEETUP_API_KEY,
        'group_id': ids,
    }

    url = '%sgroups' % config.BASE_URL
    resp = requests.get(url=url, params=params)
    data = resp.json()

    logging.info('fetched the json for a groups with ids: %s from url: %s'
                 % (meetup_ids, url))

    return data


def fetch_user_groups(meetup_id):
    """Fetch all the Meetup groups that a user belongs to."""

    params = {
        'key': config.MEETUP_API_KEY,
        'member_id': meetup_id,
    }

    url = '%sgroups' % config.BASE_URL
    resp = requests.get(url=url, params=params)
    data = resp.json()

    logging.info('fetched %s groups for member id: %s from url: %s'
                 % (len(data['results']), meetup_id, url))

    return data
