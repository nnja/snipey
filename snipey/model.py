from snipey import db

# Todo: Make meetup_ids required for meetup objects
# use an enum for snipe status


subscription_table = db.Table(
    'subscription',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer)

    subscriptions = db.relationship(
        'Group', secondary=subscription_table, backref='subscribers')

    snipes = db.relationship('Snipe', backref='user')

    token = db.Column(db.String(200))
    secret = db.Column(db.String(200))


class Snipe(db.Model):
    __tablename__ = 'snipe'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    event = db.relationship('Event')

    # todo, this should be an enum
    status = db.Column(db.String(20))


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer)

    name = db.Column(db.String(200))
    events = db.relationship('Event', backref='group', lazy='dyanmic')


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    meetup_id = db.Column(db.Integer)

    name = db.Column(db.String(200))
    rsvp_open_time = db.Column(db.DateTime)
