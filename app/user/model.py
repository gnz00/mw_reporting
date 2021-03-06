from sqlalchemy import Column, Text, DateTime, Integer, Table, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import generic_repr
from werkzeug.security import check_password_hash, generate_password_hash
from app.database import Base

# Association Table
managed_clients = Table(
    'managed_clients',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('client_id', Integer, ForeignKey('clienttable.id'))
)


@generic_repr
class User(Base):
    __searchable__ = ['alias', 'about_me']

    id = Column(Integer, primary_key=True)
    alias = Column(Text, index=True, unique=True)
    email = Column(Text, unique=True)
    avatar = Column(Text, unique=True)
    first_name = Column(Text)
    last_name = Column(Text)
    password_hash = Column(Text)
    about_me = Column(Text)
    last_seen = Column(DateTime)

    # Many to many relationship Client Managers: Clients
    clients = relationship('User',
                           secondary=managed_clients,
                           primaryjoin=(managed_clients.c.user_id == id),
                           secondaryjoin=(managed_clients.c.client_id == id),
                           backref=backref('managed_clients', lazy='dynamic'),
                           lazy='dynamic')

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @classmethod
    def get(cls, id):
        try:
            return cls.query.get(id)
        except KeyError:
            return None

    @staticmethod
    def make_unique_display_name(nickname):
        if User.query.filter_by(alias=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(alias=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def add_client(self, client):
        if not self.tracked(client, self.clients):
            self.clients.append(client)
            return self

    def remove_client(self, client):
        if self.tracked(client, self.clients):
            self.clients.append(client)
            return self

    @staticmethod
    def tracked(obj, collection):
        return obj in collection
