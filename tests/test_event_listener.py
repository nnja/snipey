from unittest import TestCase
import requests
import json
import event_listener


class EventStreamTestCase(TestCase):
    def test_successful_connection(self):
        assert event_listener.open_event_stream().status_code == 200

    def test_reconnection(self):
        pass

    def test_json_correctness(self):
        pass

    def test_subscription_exists_by_group_id(self):
        pass

    def test_create_snipe_for_one_user(self):
        pass

    def test_create_snipe_for_mult_users(self):
        pass

    def test_get_event_id(self):
        event_url = 'http://www.meetup.com/hackerschool-friends/events/128936142/'
        event_id = '128936142'
        assert event_listener.get_event_id(event_url) == event_id
