from snipey import db, event_listener
from snipey.model import Group, User

from test_snipey import SnipeyTestCase


class EventStreamTestCase(SnipeyTestCase):
    """TODO: Mock requests & responses so unit tests can be run offline
    """
    def test_successful_connection(self):
        self.assertEqual(
            event_listener.open_event_stream().status_code,
            200)

    def test_get_event_id(self):
        event_id = '128936142'
        event_url = ('http://www.meetup.com/hackerschool-friends/events/%s/'
                     % event_id)

        self.assertEqual(event_listener.get_event_id(event_url), event_id)

    # def test_create_event(self):
    #     event_id = 124211852
    #     meetup_group_id = 8230562

    #     group = Group(meetup_id=meetup_group_id)

    #     db.session.add(group)
    #     db.session.commit()

    #     event = event_listener.get_event(event_id)

    #     self.assertEqual(event.meetup_id, event_id)
    #     self.assertEqual(event.group_id, group.id)
    #     self.assertTrue(event.name)

    def test_create_snipe_for_one_user(self):
        user_id = 48598382
        event_id = 124211852
        meetup_group_id = 8230562

        event_url = ('http://www.meetup.com/hackerschool-friends/events/%s/'
                     % event_id)

        user = User(meetup_id=user_id)
        group = Group(meetup_id=meetup_group_id)
        user.subscriptions.append(group)

        db.session.add(user)
        db.session.add(group)
        db.session.commit()

        self.assertEqual(len(user.subscriptions), 1)

        event_listener.parse_snipes(meetup_group_id, event_url)

        self.assertEqual(len(user.snipes), 1)
        self.assertEqual(user.snipes[0].event.meetup_id, event_id)
        self.assertFalse(user.snipes[0].event.rsvp_open_time)

    def test_create_snipe_for_mult_users(self):
        user1_id = 48598382
        user2_id = 11111111

        event_id = 124211852
        meetup_group_id = 8230562
        event_url = ('http://www.meetup.com/hackerschool-friends/events/%s/'
                     % event_id)

        user1 = User(meetup_id=user1_id)
        user2 = User(meetup_id=user2_id)
        group = Group(meetup_id=meetup_group_id)

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(group)

        user1.subscriptions.append(group)
        user2.subscriptions.append(group)

        db.session.commit()
        self.assertEqual(len(user1.subscriptions), 1)
        self.assertEqual(len(user2.subscriptions), 1)

        event_listener.parse_snipes(meetup_group_id, event_url)

        self.assertEqual(len(user1.snipes), 1)
        self.assertEqual(len(user2.snipes), 1)

    def test_snipe_event_future_open_time(self):
        user_id = 48598382

        # event id where rsvps open in august 2014.
        event_id = 133402822
        meetup_group_id = 4064512
        event_url = 'http://www.meetup.com/ninjas/events/%s/' % event_id

        user = User(meetup_id=user_id)
        group = Group(meetup_id=meetup_group_id)

        db.session.add(user)
        db.session.add(group)
        user.subscriptions.append(group)

        db.session.commit()
        event_listener.parse_snipes(meetup_group_id, event_url)

        self.assertEqual(len(user.snipes), 1)
        self.assertEqual(user.snipes[0].event.meetup_id, event_id)

        rsvp_open_time = user.snipes[0].event.rsvp_open_time
        print rsvp_open_time
        self.assertTrue(rsvp_open_time)
        self.assertEqual(rsvp_open_time.year, 2014)
