from snipey import db
from snipey.model import User

def fetch_user(meetup_id, token_secret=()):
    """
    Fetch or create a user with the specified meetup_id from the database.

    The meetup_id must be provided.
    """
    user = User.query.filter(User.meetup_id == meetup_id).first()

    if user is None:
        user = User(meetup_id=meetup_id)
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