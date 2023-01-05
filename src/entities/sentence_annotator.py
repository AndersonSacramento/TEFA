import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey

from entities import Base


class SentenceAnnotator(Base):
    __tablename__ = 'sentence_annotator'

    status = Column(String)
    annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
    sentence_id = Column(String, ForeignKey('sentence.id'), primary_key=True)

    def __repr__(self):
        return '<SentenceAnnotator(status=%s, annotator_id=%s, sentence_id=%s)' % (self.status, self.annotator_id, self.sentence_id)


    def copy(self):
        return SentenceAnnotator(status=self.status,
                                 annotator_id=self.annotator_id,
                                 sentence_id=self.sentence_id)
