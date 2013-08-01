"""
The event listener connects to the meetup new event api stream.

For every event that comes in, check to see if we have an active
subscription in the database.  If we do, add the event to the DB, then
create a new snipe (task & database row) for every subscribed user.
Possibly in order to not interrupt the stream listening, this should
be a celery task as well.

To listen to the event stream:
r = requests.get(murl, stream=True)
for line in r.iter_lines(): # do something

To access the json:
import json
j = json.loads(line)

To access the group via json
j['groups']

To access the event url:
j['event_url']
"""
