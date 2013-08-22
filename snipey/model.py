from snipey import db, utils
from sqlalchemy.orm.exc import NoResultFound


class ReprMixin(object):
    """Hooks into SQLAlchemy's magic to make :meth:`__repr__`s.
    Source from: http://innuendopoly.org/arch/sqlalchemy-init-repr

    Any class that uses this mixin will have reprs in this format:
    Class(<col name>=<col value>,..)
    For all columns
    """
    def __repr__(self):
        def reprs():
            for col in self.__table__.c:
                yield col.name, repr(getattr(self, col.name))

        def format(seq):
            for key, value in seq:
                yield '%s=%s' % (key, value)

        args = '(%s)' % ', '.join(format(reprs()))
        classy = type(self).__name__
        return classy + args


subscription_table = db.Table(
    'subscription',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


class User(ReprMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer, index=True, unique=True)

    subscriptions = db.relationship(
        'Group', secondary=subscription_table, backref='subscribers')
    snipes = db.relationship('Snipe', backref='user')

    token = db.Column(db.String(200))
    secret = db.Column(db.String(200))


class Snipe(ReprMixin, db.Model):
    SCHEDULED = 0
    SUCCEEDED = 1
    FAILED = 2
    CANCELED = 3

    __tablename__ = 'snipe'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    event = db.relationship('Event')
    status = db.Column(db.Integer, default=SCHEDULED)
    error_msg = db.Column(db.String(200))

class Group(ReprMixin, db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer, index=True, unique=True)

    name = db.Column(db.String(200))
    events = db.relationship('Event', backref='group', lazy='dyanmic')

    @classmethod
    def from_json(cls, data):
        """ Return a list of public groups represented by the provided JSON.
        TODO: Might need timezone, but should be ok to default to Eastern.
        """
        return [cls(meetup_id=r['id'], name=r['name'])
                for r in data['results']]

    @classmethod
    def store_groups(cls, groups):
        for group in groups:
            try:
                group = Group.query.filter_by(meetup_id=group.meetup_id).one()
            except NoResultFound:
                db.session.add(group)

        db.session.commit()
        return groups


class Event(ReprMixin, db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    meetup_id = db.Column(db.String(200), index=True)

    name = db.Column(db.String(200))
    url = db.Column(db.String(200))
    rsvp_open_time = db.Column(db.DateTime)

    @classmethod
    def from_json(cls, data):
        name = data['name']

        open_time = data['rsvp_rules'].get('open_time')
        if open_time:
            open_time = utils.datetime_from_milli(open_time)

        event_id = data['id']

        group_id = data['group']['id']
        group = Group.query.filter_by(meetup_id=group_id).first()

        return cls(group=group,
                   meetup_id=event_id,
                   name=name,
                   rsvp_open_time=open_time)


class Stream(ReprMixin, db.Model):
    __tablename__ = 'stream'

    id = db.Column(db.Integer, primary_key=True)
    since_mtime_milli = db.Column(db.String(32))

    @classmethod
    def current(cls):
        stream = Stream.query.first()
        if stream is None:
            stream = Stream()
            db.session.add(stream)
        return stream
