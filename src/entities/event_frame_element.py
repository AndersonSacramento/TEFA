import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey

from entities import Base


class EventFrameElement(Base):
    __tablename__ = 'event_frame_element'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)
    frame_id = Column(Integer, ForeignKey('frame_net_event.id'))

    framenet_event = relationship("FrameNetEvent", back_populates="fes")
