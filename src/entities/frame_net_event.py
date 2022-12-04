import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime


Base = declarative_base()


class EventFN(Base):
    __tablename__ = 'event_fn'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)

    fes = relationship('EventFE', back_populates='event_fn')
