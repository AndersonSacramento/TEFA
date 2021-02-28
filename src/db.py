import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime


import uuid

engine = create_engine('sqlite:///lome_tbpt-anderson.db',  connect_args={'check_same_thread': False}, echo=True)
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

    def copy(self):
        return LemmaFN(lexunitid=self.lexunitid,
                       lemma=self.lemma,
                       pos=self.pos,
                       frameid=self.frameid,
                       lang=self.lang)


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

    def copy(self):
        return Sentence(id=self.id,
                        text=self.text,
                        document_name=self.document_name,
                        position=self.position)

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

    def copy(self):
        return EventTBPT(id=self.id,
                         eid=self.eid,
                         trigger=self.trigger,
                         lemma=self.lemma,
                         pos=self.pos,
                         start_at=self.start_at,
                         end_at=self.end_at,
                         sentence_id=self.sentence_id)

    
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
    args_ann = relationship('ArgANN', back_populates='event_ann', lazy='subquery')

    def copy(self):
        return EventANN(id=self.id,
                        event_fn_id=self.event_fn_id,
                        event_id=self.event_id,
                        created_at=self.created_at,
                        posted_at=self.posted_at,
                        updated_at=self.updated_at,
                        annotator_id=self.annotator_id)
                        
    

class ArgANN(Base):
    __tablename__ = 'arg_ann'
                      
    start_at = Column(Integer, primary_key=True)
    end_at = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    updated_at = Column(DateTime)
    event_fe_id = Column(Integer, ForeignKey('event_fe.id'), primary_key=True)
    event_ann_id = Column(String, ForeignKey('event_ann.id'), primary_key=True)
    annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
    annotator = relationship('Annotator', back_populates='args_ann')
    event_ann = relationship('EventANN', back_populates='args_ann')


    def copy(self):
        return ArgANN(start_at=self.start_at,
                      end_at=self.end_at,
                      created_at=self.created_at,
                      posted_at=self.posted_at,
                      event_fe_id=self.event_fe_id,
                      event_ann_id=self.event_ann_id,
                      annotator_id=self.annotator_id)
    
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


class ValEventANN(Base):
    __tablename__ = 'val_event_ann'

    event_ann_id = Column(String, ForeignKey('event_ann.id'), primary_key=True)
    annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
    status_type = Column(String)

    def is_wrong(self):
        return self.status_type == 'wrong'

class ValArgANN(Base):
    __tablename__ = 'val_arg_ann'

    event_ann_id = Column(String, ForeignKey('event_ann.id'), primary_key=True)
    annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
    event_fe_id = Column(String, ForeignKey('arg_ann.event_fe_id'), primary_key=True)
    status_span = Column(String)
    status_type = Column(String)
    
    def is_span_wrong(self):
        return self.status_span == 'wrong'

    def is_type_wrong(self):
        return self.status_type == 'wrong'

    def update_status_if_not_none(self, other):
        if other.status_span:
            self.status_span = other.status_span
        if other.status_type:
            self.status_type = other.status_type
    
    def __repr__(self):
        return '<ValArgANN (fe_id=%s, span=%s, type=%s)>' % (self.event_fe_id, self.status_span, self.status_type)
    
Base.metadata.create_all(engine)

