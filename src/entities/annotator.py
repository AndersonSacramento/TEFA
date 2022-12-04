import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime


Base = declarative_base()


class Annotator(Base):
    __tablename__ = 'annotator'

    email = Column(String, primary_key=True)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    
    events_ann = relationship('EventANN', back_populates='annotator')
    args_ann = relationship('ArgANN', back_populates='annotator')

    def copy(self):
        return Annotator(email=self.email,
                         created_at=self.created_at,
                         posted_at=self.posted_at)
