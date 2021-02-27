import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime


import uuid

engine = create_engine('sqlite:///lome_tbpt.db',  connect_args={'check_same_thread': False}, echo=True)
Base = declarative_base()





class TextSpan(Base):
    __tablename__ = 'text_span'

    id = Column(String, primary_key=True)
    start_at = Column(Integer)
    end_at = Column(Integer)
    annotation_id = Column(String)
    
class EventTrigger(Base):
    __tablename__ = 'event_trigger'

    id = Column(String, primary_key=True)
    source_id = Column(String)
    text = Column(String)
    sentence_id = Column(String, ForeignKey('sentence.id'))


class Sentence(Base):
    __tablename__ = 'sentence'

    id = Column(String, primary_key=True)
    text = Column(String)
    source_id = Column(String)
    document_id = Column(String, ForeignKey('document.id'))

class Document(Base):
    __tablename__ = 'document'

    id = Column(String, primary_key=True)
    name = Column(String)
    text = Column(String)
    description = Column(String)


    
class LemmaFN(Base):
    __tablename__ = 'lemma_fn'

    lexunitid = Column(Integer, primary_key=True)
    lemma = Column(String, primary_key=True)
    pos = Column(String)
    frameid = Column(Integer, primary_key=True)
    lang = Column(String)

    def __repr__(self):
        return '<LemmaFN (lexunitid=%s, lemma=%s, pos=%s)>' % (self.lexunitid, self.lemma, self.pos)


class Sentence(Base):
    __tablename__ = 'sentence'

    id = Column(String, primary_key=True)
    text = Column(String)
    document_id = Column(String, ForeignKey('document.id'))
    source_id = Column(String)


class EventTypeANN(Base):
    __tablename__ = 'event_type_ann'

    id = Column(String, primary_key=True)
    event_trigger_id = Column(String, ForeignKey('event_trigger.id'))
    event_type_id = Column(String, ForeignKey('event_type.id'))
    annotation_assignment_id = Column(String, Foreign('annotation_assignment.id'), primary_key=True)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    updated_at = Column(DateTime)

    args_ann = relationship('ArgANN', back_populates='event_ann', lazy='subquery')
    

class ArgANN(Base):
    __tablename__ = 'arg_ann'

    event_arg_type_id = Column(String, ForeignKey('event_arg_type.id'), primary_key=True)
    event_type_ann_id = Column(String, Foreign('event_type_ann.id'), primary_key=True)
    annotation_assignment_id = Column(String, Foreign('annotation_assignment.id'), primary_key=True)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    event_type_ann = relationship('EventTypeANN', back_populates='args_ann')


class EventArgType(Base):
    __tablename__ 'event_arg_type'

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    source_id = Column(String)
    event_type_model_id = Column(String, ForeignKey('eventy_type_model.id'))
    event_type_id = Column(String, ForeignKey('event_type.id'))


class EventType(Base):
    __tablename__ = 'event_type'

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    source_id = Column(String)
    event_type_model_id = Column(String, ForeignKey('event_type_model.id'))


class EventTypeModel(Base):
    __tablename__ = 'event_type_model'

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)


class AnnotationAssignment(Base):
    __tablename__ ='annotation_assignment'

    annotator_id = Column(String, ForeignKey('annotator.id'))
    sentence_id = Column(String, ForeignKey('sentence.id'))
    annotation_task_id = Column(String, ForeignKey('annotation_task.id'))
    status = Column(String)
    created_at = Column(DateTime)


class AnnotationTask(Base):
    __tablename__ = 'annotation_task'

    id = Column(String, primary_key=True)
    annotation_project_id = Column(String, ForeignKey('annotation_project.id'))
    name = Column(String)
    description = Column(String)
    task_type = Columnm(String)
    eventy_type_model_id = Column(String, ForeignKey('event_type_model.id'))
    visibility = Column(String)

class ReviewAnnotationTask(Base):
    __tablename__ = 'review_annotation_task'

    reviewed_task_id = Column(String, ForeignKey('annotation_task.id'))
    revision_task_id = Column(String, ForeignKey('annotation_task.id'))
                              
    
class AnnotationProject(Base):
    __tablename__ = 'annotation_project'

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    owner_id = Column(String, ForeignKey('annotator.id'))
    visibility = Column(String)


    
class Annotator(Base):
    __tablename__ = 'annotator'

    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime)
    posted_at = Column(DateTime)
    

class AnnotatorTask(Base):
    __tablename__ = 'annotator_task'

    annotator_id = Column(String, ForeignKey('annotator.id'))
    annotation_task_id = Column(String, ForeignKey('annotation_task.id'))
    role = Column(String)

    
Base.metadata.create_all(engine)

