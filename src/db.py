import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime


import uuid

engine = create_engine('sqlite:///tefa.db',  connect_args={'check_same_thread': False}, echo=True)
Base = declarative_base()


class LemmaFN(Base):
    __tablename__ = 'lemma_fn'

    lexunitid = Column(Integer, primary_key=True)
    lemma = Column(String, primary_key=True)
    pos = Column(String)
    frameid = Column(Integer, primary_key=True)
    lang = Column(String)

    def __repr__(self):
        return '<LemmaFN (lexunitid=%s, lemma=%s, pos=%s)>' % (self.lexunitid, self.lemma, self.pos)


class EventFN(Base):
    __tablename__ = 'event_fn'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)

    fes = relationship('EventFE', back_populates='event_fn')

class EventFE(Base):
    __tablename__ = 'event_fe'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)
    frame_id = Column(Integer, ForeignKey('event_fn.id'))

    event_fn = relationship("EventFN", back_populates="fes")

    
class Sentence(Base):
    __tablename__ = 'sentence'

    id = Column(String, primary_key=True)
    text = Column(String)
    document_name = Column(String)
    position = Column(Integer)
    events = relationship('EventTBPT', back_populates='sentence')
    timexps = relationship('TimeExpTBPT', back_populates='sentence')

class EventTBPT(Base):
    __tablename__ = 'event_tbpt'

    id = Column(String, primary_key=True)
    eid = Column(String)
    trigger = Column(String)
    lemma = Column(String)
    pos = Column(String)
    start_at = Column(Integer)
    end_at = Column(Integer)

    sentence_id = Column(String, ForeignKey('sentence.id'))
    sentence = relationship('Sentence', back_populates='events')
    
class TimeExpTBPT(Base):
    __tablename__ = 'time_exp_tbpt'

    id = Column(String, primary_key=True)
    tid = Column(String)
    text = Column(String)
    start_at = Column(Integer)
    end_at = Column(Integer)
    sentence_id = Column(String, ForeignKey('sentence.id'))
    sentence = relationship('Sentence', back_populates='timexps')
    

class EventANN(Base):
    __tablename__ = 'event_ann'

    id = Column(String, primary_key=True)
    event_fn_id = Column(Integer, ForeignKey('event_fn.id'))
    event_id = Column(String, ForeignKey('event_tbpt.id'))
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    updated_at = Column(DateTime)
    annotator_id = Column(String, ForeignKey('annotator.email'))

    annotator = relationship('Annotator', back_populates='events_ann')
    args_ann = relationship('ArgANN', back_populates='event_ann')
    

class ArgANN(Base):
    __tablename__ = 'arg_ann'
                      
    start_at = Column(Integer)
    end_at = Column(Integer)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    updated_at = Column(DateTime)
    event_fe_id = Column(Integer, ForeignKey('event_fe.id'), primary_key=True)
    event_ann_id = Column(String, ForeignKey('event_ann.id'), primary_key=True)
    annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
    annotator = relationship('Annotator', back_populates='args_ann')
    event_ann = relationship('EventANN', back_populates='args_ann')


class Annotator(Base):
    __tablename__ = 'annotator'

    email = Column(String, primary_key=True)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    
    events_ann = relationship('EventANN', back_populates='annotator')
    args_ann = relationship('ArgANN', back_populates='annotator')
            
class SentenceAnnotator(Base):
    __tablename__ = 'sentence_annotator'

    status = Column(String)
    annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
    sentence_id = Column(String, ForeignKey('sentence.id'), primary_key=True)

    def __repr__(self):
        return '<SentenceAnnotator(status=%s, annotator_id=%s, sentence_id=%s)' % (self.status, self.annotator_id, self.sentence_id)
Base.metadata.create_all(engine)

