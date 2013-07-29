from snipey import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer)

    token = db.Column(db.String(200))
    secret = db.Column(db.String(200))

    subscriptions = relationship('Subscription', backref='user', lazy='dynamic')

class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer)

    name = db.Column(db.String(200))
    events = relationship('Event', backref='group', lazy='dyanmic')

class Subscription(db.Model):
    __tablename__ = 'subscription'

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    group_id = db.Column(db.Integer, ForeignKey('group.id'))

    snipes = relationship('Snipe', backref='subscription', lazy='dynamic')

class Snipe(db.Model):
    __tablename__ = 'snipe'

    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, ForeignKey('subscription.id'))
    event_id = db.Column(db.Integer, ForeignKey('event.id'))

    status = db.Column(db.String(20)) # todo, this should be an enum

class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)

    meetup_id = db.Column(db.Integer)
    group_id = db.Column(db.Integer, ForeignKey('group.id'))

    name = db.Column(db.String(200))

