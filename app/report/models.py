from sqlalchemy import Column, Text, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr
from app.database import Base


@generic_repr
class CallTable(Base):
    __searchable__ = []

    """
    Parent table
    """
    call_id = Column(Integer, primary_key=True)
    call_direction = Column(Integer)
    calling_party_number = Column(Text)
    dialed_party_number = Column(Text)
    account_code = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    system_id = Column(Integer)
    caller_id = Column(Text)

    # parent-child relationship
    events = relationship("EventTable", back_populates='call_id')   # Iterable of EventTable objects

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @staticmethod
    def src_statement(request_date):
        """Get src rows by running select * from table_name"""
        return """SELECT * FROM c_call WHERE to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}'""".format(
            date=request_date
        )


@generic_repr
class EventTable(Base):
    __searchable__ = []

    """
    Child table
    """
    event_id = Column(Integer, primary_key=True)
    event_type = Column(Integer, nullable=False)
    calling_party = Column(Text)
    receiving_party = Column(Text)
    hunt_group = Column(Text)
    is_conference = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    tag = Column(Text)
    recording_rule = Column(Integer)

    # parent-child relationship
    call_id = Column(Integer, ForeignKey('calltable.call_id'))
    call = relationship("CallTable", back_populates="events")   # Stores the parent object by the ForeignKey

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @staticmethod
    def src_statement(request_date):
        """Get src rows by running select * from table_name"""
        return """SELECT * FROM c_event WHERE to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}'""".format(
            date=request_date
        )