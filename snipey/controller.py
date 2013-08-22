from snipey import db, meetup
from snipey.model import User, Group, Snipe


def fetch_user(meetup_id, token_secret=(), name=None):
    """
    Fetch or create a user with the specified meetup_id from the database.

    The meetup_id must be provided.
    """
    user = User.query.filter(User.meetup_id == meetup_id).first()

    if user is None:
        user = User(meetup_id=meetup_id)
        db.session.add(user)

    update_user_credentials(user, token_secret)
    #user.name = name
    db.session.commit()

    return user


def update_user_credentials(user, token_secret):
    """
    If a user's oauth credentials have changed, update them in the database
    """
    if token_secret and (user.token, user.secret) != token_secret:
        user.token, user.secret = token_secret


def unsubscribe_from_group(user, group):
    """
    Unsubscribe a user from a given meetup group.

    When the user unsubscribes, cancel all pending snipes for this group
    TODO: Decide how to handle exceptions
    """
    try:
        snipes = Snipe.query.join(
            User.subscriptions).filter(Group.id == group.id).all()
        user.subscriptions.remove(group)

        for snipe in snipes:
            if snipe.status == Snipe.SCHEDULED:
                snipe.status = Snipe.CANCELED

        db.session.commit()
    except ValueError:
        pass


def subcribe_to_groups(user, meetup_ids):
    """
    Subscribe a user to the given meetup groups based on meetup id.

    If a Group with the provided meetup_id doesn't exist, create
    it.
    """
    data = meetup.fetch_groups(meetup_ids)
    groups = Group.from_json(data)
    Group.store_groups(groups)

    subscribed_groups = [group.meetup_id for group in user.subscriptions]
    for group in groups:
        if group.meetup_id not in subscribed_groups:
            user.subscriptions.append(
                Group.query.filter_by(meetup_id=group.meetup_id).first())

    db.session.commit()


def get_group_list(user):
    """
    Get a list of pair (meetup_id, group name) for every
    Meetup group that a User belongs to.
    """
    if user is None:
        return []

    results = meetup.fetch_user_groups(user.meetup_id)['results']
    return [(result['id'], result['name']) for result in results
            if result['visibility'] == 'public']
