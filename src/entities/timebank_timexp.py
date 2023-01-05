import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey

from entities import Base


class TimebankTimexp(Base):
    __tablename__ = 'timebank_timexp'

    id = Column(String, primary_key=True)
    tid = Column(String)
    text = Column(String)
    start_at = Column(Integer)
    end_at = Column(Integer)
    sentence_id = Column(String, ForeignKey('sentence.id'))
    sentence = relationship('Sentence', back_populates='timexps')
