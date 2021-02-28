from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sqlalchemy

import math

from db import SentenceAnnotator, Annotator, LemmaFN, EventTBPT, Sentence, EventANN, ArgANN, Base



def partitions(data, config, common_percent=10):
    config = sorted(config, key=lambda c: c[1])
    data_len = len(data)
    end_at = math.ceil(data_len * (common_percent/100))
    common = data[:end_at]

    start_at = end_at 
    for (_,percent) in config:
        start_at = end_at
        end_at += math.ceil(data_len * ((percent - common_percent)/100))
        if end_at > data_len:
            start_at -= (end_at - data_len)
            end_at = data_len
        print(data[start_at:end_at] + common)




from contextlib import contextmanager

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        

def create_partition(dbpath, config, common_percent=10):
    "config = [ (sd@mail, 34), (f@mail: 50)}"
    global Session


    main_engine = create_engine('sqlite:///%s' % dbpath, echo=False)
    Base.metadata.create_all(main_engine)
    Session = sessionmaker(bind=main_engine, expire_on_commit=False)
    main_session =  Session()
    
    all_events = main_session.query(EventTBPT).all()

    events_len = len(all_events)
    print('len events %d' % events_len)

    config = sorted(config, key=lambda c: c[1])

    end_at = math.ceil(events_len * (common_percent/100))
    common_events = all_events[:end_at]

    db_name = dbpath.split('.db')[0]
    common_engine = create_engine('sqlite:///%s-common.db' % db_name, echo=True)
    SessionCommon = sessionmaker(bind=common_engine)
    common_session = SessionCommon()
    Base.metadata.create_all(common_engine)

    persist_all_sentences_from(common_events, common_session)
    persist_all_events_from(common_events, common_session)
    persist_all_lemma_fn(common_session)
    annotator = Annotator(email='common@mail')
    persist_annotator(annotator, common_session)
    persist_all_events_ann_from(common_events, annotator, common_session)
    persist_all_args_ann_from(common_events, annotator, common_session)

    common_session.commit()
    common_session.close()

    start_at = end_at
    for (email, percent) in config:
        start_at = end_at
        end_at += math.ceil(events_len * ((percent - common_percent)/100))

        if end_at > events_len:
            start_at -= (end_at - events_len)
            end_at = events_len
            
        femail = email.split('@')[0]
        cur_engine = create_engine('sqlite:///%s-%s.db' % (db_name, femail), echo=True)
        CurSession = sessionmaker(bind=cur_engine)
        cur_session =  CurSession()
        Base.metadata.create_all(cur_engine)
        
        cur_events = all_events[start_at:end_at] +  common_events

        persist_all_sentences_from(cur_events, cur_session)
        persist_all_events_from(cur_events, cur_session)
        persist_all_lemma_fn(cur_session)
        annotator = Annotator(email=email)
        persist_annotator(annotator, cur_session)
        persist_all_events_ann_from(cur_events, annotator, cur_session)
        persist_all_args_ann_from(cur_events, annotator, cur_session)

        cur_session.commit()
        cur_session.close()        
        
        
        

def query_all_sentences_from(events):
    sentences = []
    sentences_ids = {event.sentence_id for event in events}
    with session_scope() as session:
        sentences =  session.query(Sentence).\
            filter(Sentence.id.in_(sentences_ids)).\
            all()
    print('sentence size %d' % len(sentences))
    return sentences


def query_all_events_ann_from(events):
    events_ann = []
    events_ids = {event.id for event in events}
    with session_scope() as session:
        events_ann =  session.query(EventANN).\
            filter(EventANN.event_id.in_(events_ids)).\
            all()
    return events_ann


def query_all_events_args_ann_from(events):
    args_ann = []
    events_ids = {event.id for event in events}
    with session_scope() as session:
        args_ann = session.query(ArgANN).\
            join(EventANN, EventANN.id==ArgANN.event_ann_id).\
            join(EventTBPT, EventANN.event_id==EventTBPT.id).\
            filter(EventTBPT.id.in_(events_ids)).\
            all()
    return args_ann

def query_all_lemma():
    lemmas = []
    with session_scope() as session:
        lemmas = session.query(LemmaFN).all()
    return lemmas


def persist_all_events_from(events, session):
    events_ids = list({event.id for event in events})
    for event in events:
        if event.id in events_ids:
            session.add(event.copy())
            events_ids.remove(event.id)
    session.commit()

def persist_all_lemma_fn(session):
    for lemma in query_all_lemma():
        session.add(lemma.copy())
    session.commit()
    
def persist_all_sentences_from(events, session):
    for sentence in query_all_sentences_from(events):
        session.add(sentence.copy())
    session.commit()

def persist_annotator(annotator, session):
    session.add(annotator)
    for sentence in session.query(Sentence).all():
        session.add(SentenceAnnotator(annotator_id=annotator.email,
                                      sentence_id=sentence.id,
                                      status='todo'))
    session.commit()

def persist_all_events_ann_from(events, annotator, session):
    for event_ann in query_all_events_ann_from(events):
        event_ann = event_ann.copy()
        event_ann.annotator_id = annotator.email
        session.add(event_ann)
    session.commit()

def persist_all_args_ann_from(events, annotator, session):
    for arg_ann in query_all_events_args_ann_from(events):
        arg_ann = arg_ann.copy()
        arg_ann.annotator_id = annotator.email
        session.add(arg_ann)
    session.commit()
