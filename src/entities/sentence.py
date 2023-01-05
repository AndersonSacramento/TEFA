import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime

from entities import Base


class Sentence(Base):
    __tablename__ = 'sentence'

    id = Column(String, primary_key=True)
    text = Column(String)
    document_name = Column(String)
    position = Column(Integer)
    events = relationship('TimebankEvent', back_populates='sentence')
    timexps = relationship('TimebankTimexp', back_populates='sentence')

    def copy(self):
        return Sentence(id=self.id,
                        text=self.text,
                        document_name=self.document_name,
                        position=self.position)
