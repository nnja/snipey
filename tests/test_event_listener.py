from snipey import app, db, controller
from test_snipey import SnipeyTestCase
from snipey.model import Group
import json
import event_listener

TEST_JSON = """{"rsvp_limit":0,"status":"upcoming","visibility":"public","maybe_rsvp_count":0,"payment_required":"0","mtime":1375729719944,"venue":{"zip":"33351","lon":-80.251999,"name":"Indian Chillies","state":"FL","address_1":"4465 N University Dr","lat":26.180737,"country":"us","city":"Lauderhill"},"id":"133216242","utc_offset":-14400000,"time":1377360000000,"venue_visibility":"public","yes_rsvp_count":1,"event_url":"http:\/\/www.meetup.com\/SouthBeachBollywood\/events\/133216242\/","description":"<p>Let's get together and catch up.<\/p>\n\n","name":"Lunch at Indian Chillies","group":{"id":1502533,"group_lat":25.78,"name":"Indian Food, Bollywood Music and Movies in Miami","state":"FL","group_lon":-80.14,"join_mode":"open","urlname":"SouthBeachBollywood","country":"us","city":"Miami Beach"}}""".strip()


class EventStreamTestCase(SnipeyTestCase):
    def test_successful_connection(self):
        self.assertEqual(
            event_listener.open_event_stream().status_code,
            200)

    def test_get_event_id(self):
        event_id = '128936142'
        event_url = ('http://www.meetup.com/hackerschool-friends/events/%s/'
                     % event_id)

        self.assertEqual(event_listener.get_event_id(event_url), event_id)

    def test_create_event(self):
        event_id = 124211852
        meetup_group_id = 8230562

        group = Group(meetup_id=meetup_group_id)

        db.session.add(group)
        db.session.commit()

        event = event_listener.create_event(group, event_id)

        self.assertEqual(event.meetup_id, event_id)
        self.assertEqual(event.group_id, group.id)
        self.assertTrue(event.name)

    def test_create_snipe_for_one_user(self):
        data = json.loads(TEST_JSON)

        meetup_group_id = data['group']['id']
        event_url = data['event_url']
        
        user = User(meetup_id='1235')
        group = Group(meetup_id=meetup_group_id)

        db.session.add(user)
        db.session.add(group)
        
        controller.subscribe_to_group(user, group)

        self.assertEqual(len(user.subscriptions), 1)

    def test_create_snipe_for_mult_users(self):
        pass
