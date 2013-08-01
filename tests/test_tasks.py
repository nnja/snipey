"""
Test Celery Tasks

1. Test RSVP:
    Given a token, secret, and event id RSVP to the event.

    Store the results in a backend.

    Possible Errors:
        1. The token and secret are invalid
        2. The token and secret combo are unauthorized to RSVP to this event
        3. RSVPs aren't open.
        4. Others....

2. Test RSVP Later:
    Given a snipe ID and a RSVP eta, RSVP to the event at a later date.

"""