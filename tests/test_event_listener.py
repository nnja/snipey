from snipey import app, db, controller
from test_snipey import SnipeyTestCase
from snipey.model import Group, User
import json
import event_listener


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
        user_id = 48598382
        event_id = 124211852
        meetup_group_id = 8230562

        event_url = 'http://www.meetup.com/hackerschool-friends/events/%s/' % event_id

        user = User(meetup_id=user_id)
        group = Group(meetup_id=meetup_group_id)

        db.session.add(user)
        db.session.add(group)
        
        controller.subscribe_to_group(user, group)

        self.assertEqual(len(user.subscriptions), 1)

        event_listener.parse_snipes(meetup_group_id, event_url)

        self.assertEqual(len(user.snipes), 1)
        self.assertEqual(user.snipes[0].event.meetup_id, event_id)

    def test_create_snipe_for_mult_users(self):
        user1_id = 48598382
        user2_id = 48598392
        
        event_id = 124211852
        meetup_group_id = 8230562
        event_url = 'http://www.meetup.com/hackerschool-friends/events/%s/' % event_id

        user1 = User(meetup_id=user1_id)
        user2 = User(meetup_id=user2_id)
        group = Group(meetup_id=meetup_group_id)

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(group)

        controller.subscribe_to_group(user1, group)
        controller.subscribe_to_group(user2, group)

        self.assertEqual(len(user1.subscriptions), 1)
        self.assertEqual(len(user2.subscriptions), 1)

        event_listener.parse_snipes(meetup_group_id, event_url)

        self.assertEqual(len(user1.snipes), 1)
        self.assertEqual(len(user2.snipes), 1)
