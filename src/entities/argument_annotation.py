import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey

from entities import Base


class ArgumentAnnotation(Base):
    __tablename__ = 'argument_annotation'
    
    start_at = Column(Integer, primary_key=True)
    end_at = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    updated_at = Column(DateTime)
    #event_fe_id = Column(Integer, ForeignKey('event_frame_element.id'),
    #                     primary_key=True)
    event_ann_id = Column(String, ForeignKey('event_annotation.id'), primary_key=True)
    annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
    annotator = relationship('Annotator', back_populates='args_ann')


    def copy(self):
        return ArgumentAnnotation(start_at=self.start_at,
                                  end_at=self.end_at,
                                  created_at=self.created_at,
                                  posted_at=self.posted_at,
                                  event_fe_id=self.event_fe_id,
                                  event_ann_id=self.event_ann_id,
                                  annotator_id=self.annotator_id)
    
