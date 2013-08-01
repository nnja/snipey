from snipey import db, model


def fetch_user(meetup_id, token_secret=()):
    """
    Fetch or create a user with the specified meetup_id from the database.

    The meetup_id must be provided.
    """
    user = model.User.query.filter(model.User.meetup_id == meetup_id).first()

    if user is None:
        user = model.User(meetup_id=meetup_id)
        db.session.add(user)

    update_user_credentials(user, token_secret)
    db.session.commit()

    return user


def update_user_credentials(user, token_secret):
    """
    If a user's oauth credentials have changed, update them in the database
    """
    if token_secret and (user.token, user.secret) != token_secret:
        user.token, user.secret = token_secret


def subscribe_to_group(user, group):
    """
    Subscribe a user to the provided meetup group.
    """
    subscription = model.Subscription(user=user, group=group)
    db.session.add(subscription)
    db.session.commit()
    return subscription


def unsubscribe_from_group(user, group):
    """
    Unsubscribe a user from a given meetup group.

    When the user ubsubscribes, remove all pending snipes for this group,
    TODO: cancel any associated celery tasks
    TODO: throw an exception if no matching subscription is found
    """

    subscription = model.Subscription.query.filter(
        model.Subscription.user_id == user.id,
        model.Subscription.group_id == group.id).first()

    db.session.delete(subscription)
    db.session.commit()
