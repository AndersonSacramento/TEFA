import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey

from entities import Base


class TimebankEvent(Base):
    __tablename__ = 'timebank_event'

    id = Column(String, primary_key=True)
    eid = Column(String)
    trigger = Column(String)
    lemma = Column(String)
    pos = Column(String)
    start_at = Column(Integer)
    end_at = Column(Integer)

    sentence_id = Column(String, ForeignKey('sentence.id'))
    sentence = relationship('Sentence', back_populates='events')


    def __repr__(self):
        return '<TimebankEvent (trigger=%s, start=%s, end=%s)>' % (self.trigger, self.start_at, self.end_at)
    
    def copy(self):
        return TimebankEvent(id=self.id,
                         eid=self.eid,
                         trigger=self.trigger,
                         lemma=self.lemma,
                         pos=self.pos,
                         start_at=self.start_at,
                         end_at=self.end_at,
                         sentence_id=self.sentence_id)

