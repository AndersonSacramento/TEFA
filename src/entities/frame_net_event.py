import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime

from entities import Base


class FrameNetEvent(Base):
    __tablename__ = 'frame_net_event'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)

    fes = relationship('EventFrameElement', back_populates='framenet_event')
