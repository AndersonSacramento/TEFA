import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey

from entities import Base


class EventAnnotation(Base):
    __tablename__ = 'event_annotation'

    id = Column(String, primary_key=True)
    frame_id = Column(Integer, ForeignKey('frame_net_event.id'))
    event_id = Column(String, ForeignKey('timebank_event.id'))
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    updated_at = Column(DateTime)
    annotator_id = Column(String, ForeignKey('annotator.email'))

    annotator = relationship('Annotator', back_populates='events_ann')
    args_ann = []#relationship('ArgANN', back_populates='event_ann')#, lazy='subquery')

    def copy(self):
        return EventAnnotation(id=self.id,
                        frame_id=self.frame_id,
                        event_id=self.event_id,
                        created_at=self.created_at,
                        posted_at=self.posted_at,
                        updated_at=self.updated_at,
                        annotator_id=self.annotator_id)
