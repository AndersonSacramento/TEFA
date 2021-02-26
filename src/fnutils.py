from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
import sqlalchemy
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

import timebankpttoolkit.timebankptcorpus as timebankpt
from datetime import datetime, timezone
import uuid

from db import SentenceAnnotator, Annotator, LemmaFN, EventTBPT, TimeExpTBPT, Sentence, EventANN, ArgANN, engine


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


def create_session():
    global Session
    Session = sessionmaker(bind=engine, expire_on_commit=False)

def now():
    return datetime.now(timezone.utc)

def create_annotator(email):
    with session_scope() as session:
        annotator = Annotator(email=email, created_at=now())
        session.add(annotator)
    create_all_sentence_annotator(annotator)
    return annotator



def delete_previous(event_ann, args_ann):
    with session_scope() as session:
        session.query(EventANN).filter(EventANN.event_id==event_ann.event_id, EventANN.annotator_id==event_ann.annotator_id).\
            delete(synchronize_session='fetch')
        for arg_ann in args_ann:
            session.query(ArgANN).filter(ArgANN.event_fe_id==arg_ann.event_fe_id, ArgANN.event_ann_id==arg_ann.event_ann_id, ArgANN.annotator_id==arg_ann.annotator_id).\
                delete(synchronize_session='fetch')

    
def save_event_ann(event_ann):
    with session_scope() as session:
        session.add(event_ann)


def save_args_ann(args_ann):
    with session_scope() as session:
        for arg_ann in args_ann:
            session.add(arg_ann)


def create_all_sentence_annotator(annotator):
    with session_scope() as session:
        for sentence in session.query(Sentence).all():
            session.add(SentenceAnnotator(annotator_id=annotator.email,
                                      sentence_id=sentence.id,
                                      status='todo'))


    
def get_all_annotators():
    annotators = []
    with session_scope() as session:
         annotators = session.query(Annotator).all()
    return annotators

def query_lemma(lemma_name):
    lemmas_fn = []
    with session_scope() as session:
        lemmas_fn = session.query(LemmaFN).filter_by(lemma=lemma_name).all()
    return lemmas_fn

def query_frameid(lemma_name):
    frames_id = []
    with session_scope() as session:
        frames_id = {out[0] for out in session.query(LemmaFN.frameid).filter_by(lemma=lemma_name).all()}
    return frames_id

def frame_by_id(frame_id):
    return fn.frame(frame_id)

def query_sentence_by(sentence_id):
    sentence = None
    with session_scope() as session:
        sentence = session.query(Sentence).filter_by(id=sentence_id).first()
    return sentence

def find_event_ann(events_ann, event_id):
    for e_ann in events_ann:
        if e_ann.event_id == event_id:
            return e_ann

def find_fe(fes, fe_name):
    for fe in fes:
        if fe.name == fe_name:
            return fe
        
def query_events_sentence(sentence):
    events = []
    with session_scope() as session:
        events = session.query(EventTBPT).filter_by(sentence_id=sentence.id).all()
    return events

def query_events_ann(annotator_id, events_tbpt_ids):
    events_ann = []
    with session_scope() as session:
        events_ann = session.query(EventANN).filter(EventANN.event_id.in_(events_tbpt_ids)).filter_by(annotator_id=annotator_id).all()
    return events_ann


def load_sentences(annotator_id, status):
    sentences = []
    with session_scope() as session:
        sentences = session.query(Sentence).\
            join(SentenceAnnotator, Sentence.id==SentenceAnnotator.sentence_id).\
            join(Annotator, Annotator.email==SentenceAnnotator.annotator_id).\
            filter(SentenceAnnotator.status==status,
                   SentenceAnnotator.annotator_id==annotator_id).\
            all()
    #session.commit()
    return sentences
    
def change_sentence_status(sentence, email, status):
    with session_scope() as session:
        sentence_annotator = session.query(SentenceAnnotator).filter_by(annotator_id=email, sentence_id=sentence.id).first()
        if sentence_annotator:
            sentence_annotator.status = status
        print(sentence_annotator)


    
def str_uuid():
    return str(uuid.uuid4())
    
def load_timebankpt_data(corpus_dir):
    session = Session()
    corpus = timebankpt.TimeBankPTCorpus('tbpt', corpus_dir)
    for (doc_name, doc) in corpus.documents_by_target().items():
        for (i, sent) in enumerate(doc.get_sentences()):
            if not sent.has_events(): continue
            sent_id = str_uuid()
            sentence = Sentence(id=sent_id, text=sent.get_text(), document_name=doc_name, position=i)
            session.add(sentence)
            for ((start_at, end_at), event) in sent.get_events_locations():
                event_tbpt = EventTBPT(id=str_uuid(), eid=event.get_id(), trigger=event.text, lemma=event.get_stem(), pos=event.get_pos(), start_at=start_at, end_at=end_at, sentence_id=sent_id)
                session.add(event_tbpt)
            for ((start_at, end_at), timexp) in sent.get_timexs_locations():
                time_exp_tbpt = TimeExpTBPT(id=str_uuid(), tid=timexp.get_id(), text=timexp.get_text(), start_at=start_at, end_at=end_at, sentence_id=sent_id)
                session.add(time_exp_tbpt)
            session.commit()
            
    
def load_fn_events_lemmas():
    Session = sessionmaker(bind=engine)
    session = Session()
    for lemma_fn in lemma_frames():
        session.add(lemma_fn)
    session.commit()

def is_event(frame):
    if frame and frame.name == 'Event':
        return frame
    elif frame:
        for rel in filter_inheritance(frame):
            parcial_r = is_event(rel.Parent)
            if parcial_r:
                return parcial_r

def filter_inheritance(frame):
    return [rel for rel in frame.frameRelations if rel.type.name == 'Inheritance' and frame.name == rel.Child.name]

def filter_core_fe(frame):
    return [fe for fe in frame.FE.values() if fe.coreType == 'Core']



def fn_to_wn_pos(notation):
    return {'n': wn.NOUN,
            'v': wn.VERB,
            'a': wn.ADJ }.get(notation, notation)

def get_lemma_from_lexunit_name(lexunit_name, lang='por'):
    name, pos = lexunit_name.split('.')
    pos = fn_to_wn_pos(pos)
    try:
        return {name for lemma in wn.synsets(name, pos) for name in lemma.lemma_names(lang=lang)}
    except KeyError:
        return {}
    
def all_event_frames():
    lframes = []
    for frame in fn.frames():
        if frame:
            if not is_event(frame): continue
            lframes.append(frame)
    return lframes
        
def lemma_frames(lang='por'):
    for frame in fn.frames():
        if not is_event(frame): continue
        for lexunit in frame.lexUnit.values():
            print(lexunit.name)
            _ , pos = lexunit.name.split('.')
            pos = fn_to_wn_pos(pos)
            for lemma_name in get_lemma_from_lexunit_name(lexunit.name, lang=lang):
                yield LemmaFN(lexunitid=lexunit.ID,
                              lemma=lemma_name,
                              pos=pos,
                              frameid=frame.ID,
                              lang=lang)
                # {'lexunit_id': lexunit.ID,
                #  'lemma_name': lemma_name,
                #  'pos': pos,
                #  'fn_id': frame.ID,
                #  'lang': lang}
                
