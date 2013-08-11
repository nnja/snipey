from snipey import app, db, controller
from snipey.model import User, Group
from flask.ext.testing import TestCase


class SnipeyTestCase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['CSRF_ENABLED'] = False
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()
        db.session.remove()


class UserTestCase(SnipeyTestCase):
    def test_fetch_user(self):
        """
        1. calling controller.fetch_user without providing a token or
        secret does not modify the user's existing token or secret
        """

        user = User(meetup_id='1234', token='old_token', secret='old_secret')
        db.session.add(user)
        db.session.commit()

        fetched_user = controller.fetch_user(meetup_id='1234')
        assert user.id == fetched_user.id
        assert user.token, user.secret == ('old_token', 'old_secret')

    def test_fetch_user_update_token_secret(self):
        """
        2. calling controller.fetch_user and providing an updated token and
        secret updates them in the database
        """

        user = User(meetup_id='1234', token='old_token', secret='old_secret')
        db.session.add(user)
        db.session.commit()

        fetched_user = controller.fetch_user(
            meetup_id='1234', token_secret=('new_token', 'new_secret'))
        assert user.id == fetched_user.id
        assert user.token, user.secret == ('new_token', 'new_secret')

    def test_fetch_new_user(self):
        """
        3. calling controller.fetch_user for a user with a meetup_id that
        is not in the database returns a newly created user
        """

        meetup_id = '1243483483'
        assert not User.query.filter(User.meetup_id == meetup_id).first()

        user = controller.fetch_user(
            meetup_id=meetup_id, token_secret=('new_token', 'new_secret'))
        assert user

        assert User.query.filter(User.meetup_id == meetup_id).first()


class SubscribeTestCase(SnipeyTestCase):
    """
    Given a user and a group, add a subscription to the database.
    """
    def test_subscription(self):
        user = User(meetup_id='1234')
        group = Group(meetup_id='5678')
        user.subscriptions.append(group)

        db.session.add(user)
        db.session.add(group)

        db.session.commit()

        assert len(user.subscriptions) == 1
        assert user.subscriptions[0] == group


class UnsubcribeTestCase(SnipeyTestCase):
    """
    Given a user and a group, remove a subscription from the database.

    Make sure that removing the subscription leaves both the User and
    the Group in the database

    Any scheduled snipes should be removed as well, and if any celery
    tasks exist for those snipes they should be canceled/recalled.

    """
    def test_unsubscribe(self):
        user = User(meetup_id='1234')
        group = Group(meetup_id='5678')
        user.subscriptions.append(group)

        db.session.add(user)
        db.session.add(group)

        db.session.commit()

        assert len(user.subscriptions) == 1

        controller.unsubscribe_from_group(user, group)
        assert len(user.subscriptions) == 0

        assert len(Group.query.filter(Group.id == group.id).all()) == 1
        assert len(User.query.filter(User.id == user.id).all()) == 1
