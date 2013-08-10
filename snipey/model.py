from snipey import db
# Todo: Make meetup_ids required for meetup objects
# use an enum for snipe status


class ReprMixin(object):
    """Hooks into SQLAlchemy's magic to make :meth:`__repr__`s.
    Source from: http://innuendopoly.org/arch/sqlalchemy-init-repr
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
    meetup_id = db.Column(db.Integer)

    name = db.Column(db.String(200))
    subscriptions = db.relationship(
        'Group', secondary=subscription_table, backref='subscribers')

    snipes = db.relationship('Snipe', backref='user')

    token = db.Column(db.String(200))
    secret = db.Column(db.String(200))


class Snipe(ReprMixin, db.Model):
    SCHEDULED = 1
    SUCCEEDED = 2
    FAILED = 3

    __tablename__ = 'snipe'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    event = db.relationship('Event')

    # TODO: look at sqlalchemy support for enums
    status = db.Column(db.String(20), default=SCHEDULED)


class Group(ReprMixin, db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer)

    name = db.Column(db.String(200))
    events = db.relationship('Event', backref='group', lazy='dyanmic')


class Event(ReprMixin, db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    meetup_id = db.Column(db.Integer)

    name = db.Column(db.String(200))
    rsvp_open_time = db.Column(db.DateTime)
