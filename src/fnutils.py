from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
import sqlalchemy
from sqlalchemy import create_engine
import _thread

from sqlalchemy.orm import sessionmaker

#import timebankpttoolkit.timebankptcorpus as timebankpt
from datetime import datetime, timezone
import uuid

from db import SentenceAnnotator, Annotator, LemmaFN, EventTBPT, TimeExpTBPT, Sentence, EventANN, ArgANN
import db

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


def create_session(dbpath='lome_tbpt.db'):
    global Session
    global engine
    
    engine = create_engine('sqlite:///%s' % (dbpath),  connect_args={'check_same_thread': False}, echo=False)

    db.Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    get_all_event_or_state_frames()

def now():
    return datetime.now(timezone.utc)

def create_annotator(email):
    with session_scope() as session:
        annotator = Annotator(email=email, created_at=now())
        session.add(annotator)
    create_all_sentence_annotator(annotator)
    return annotator


def delete_arg_ann(arg_ann):
    with session_scope() as session:
        session.query(ArgANN).filter(ArgANN.event_fe_id==arg_ann.event_fe_id, ArgANN.event_ann_id==arg_ann.event_ann_id, ArgANN.annotator_id==arg_ann.annotator_id, ArgANN.start_at==arg_ann.start_at, ArgANN.end_at==arg_ann.end_at).\
            delete(synchronize_session='fetch')

        
def delete_previous(event_ann, args_ann):
    with session_scope() as session:
        session.query(EventANN).filter(EventANN.event_id==event_ann.event_id, EventANN.annotator_id==event_ann.annotator_id).\
            delete(synchronize_session='fetch')
        for arg_ann in args_ann:
            session.query(ArgANN).filter(ArgANN.event_fe_id==arg_ann.event_fe_id, ArgANN.event_ann_id==arg_ann.event_ann_id, ArgANN.annotator_id==arg_ann.annotator_id).\
                delete(synchronize_session='fetch')


def save_val_event(val_event_ann):
    with session_scope() as session:
        if val_event_ann.is_wrong():
            # delete all the args
            session.query(ValArgANN).filter(ValArgANN.event_ann_id==val_event_ann.event_ann_id, ValArgANN.annotator_id==val_event_ann.annotator_id).delete(synchronize_session='fetch')
        session.query(ValEventANN).filter(ValEventANN.event_ann_id==val_event_ann.event_ann_id, ValEventANN.annotator_id==val_event_ann.annotator_id).delete(synchronize_session='fetch')
        session.add(val_event_ann)

def query_val_event(event_ann_id, annotator_id):
    val_event = None
    with session_scope() as session:
        val_event = session.query(ValEventANN).filter_by(event_ann_id=event_ann_id, annotator_id=annotator_id).first()
    return val_event

def query_val_args(event_ann_id, annotator_id):
    vals_args = []
    with session_scope() as session:
        vals_args = session.query(ValArgANN).filter_by(event_ann_id=event_ann_id, annotator_id=annotator_id).all()
    return vals_args

def delete_val_arg(event_ann_id, annotator_id, event_fe_id):
    with session_scope() as session:
        session.query(ValArgANN).filter_by(event_ann_id=event_ann_id, annotator_id=annotator_id, event_fe_id=event_fe_id).delete(synchronize_session='fetch')

def query_val_arg(event_ann_id, annotator_id, event_fe_id, session=None):
    if session:
        return session.query(ValArgANN).filter_by(event_ann_id=event_ann_id, annotator_id=annotator_id, event_fe_id=event_fe_id).first()
    else:
        val_arg = None
        with session_scope() as session:
            val_arg = session.query(ValArgANN).filter_by(event_ann_id=event_ann_id, annotator_id=annotator_id, event_fe_id=event_fe_id).first()
        return val_arg

def save_val_arg(val_arg_ann):
    with session_scope() as session:
        val_event = query_val_event(val_arg_ann.event_ann_id, val_arg_ann.annotator_id)
        if val_event:
            if not val_event.is_wrong():
                previous_val_arg = query_val_arg(val_event.event_ann_id, val_arg_ann.annotator_id, val_arg_ann.event_fe_id, session=session)
                if not previous_val_arg:
                    session.add(val_arg_ann)
                else:
                    previous_val_arg.update_status_if_not_none(val_arg_ann)
                print('val %s' % previous_val_arg)
        else:
            previous_val_arg = query_val_arg(val_event.event_ann_id, val_arg_ann.annotator_id, val_arg_ann.event_fe_id, session=session)
            if not previous_val_arg:
                session.add(val_arg_ann)
            else:
                previous_val_arg.update_status_if_not_none(val_arg_ann)
                print('no val %s' % previous_val_arg)
            #delete_val_arg(val_event.event_ann_id, val_arg_ann.annotator_id, val_arg_ann.event_fe_id)
            #session.add(val_arg_ann)

    
def save_event_ann(event_ann):
    with session_scope() as session:
        session.add(event_ann)

def save_arg_ann(arg_ann):
    with session_scope() as session:
        session.add(arg_ann)
        
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


    
def get_all_annotators(notin_emails=[]):
    annotators = []
    with session_scope() as session:
         annotators = session.query(Annotator).\
             filter(Annotator.email.notin_(notin_emails)).\
             all()
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


def find_unique_annotator():
    annotator = None
    with session_scope() as session:
        annotator = session.query(Annotator).first()
    return annotator


def frame_by_id(frame_id):
    return fn.frame(frame_id)

def query_sentence_by(sentence_id):
    sentence = None
    with session_scope() as session:
        sentence = session.query(Sentence).filter_by(id=sentence_id).first()
    return sentence

def query_sentence_by_event_id(id):
    sentence = None
    with session_scope() as session:
        sentence = session.query(Sentence).\
            join(EventTBPT, Sentence.id==EventTBPT.sentence_id).\
            join(EventANN, EventANN.event_id==EventTBPT.id).\
            filter(EventANN.id==id).\
            first()
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

def query_event_tbpt(event_id):
    event = None
    with session_scope() as session:
        event = session.query(EventTBPT).filter_by(id=event_id).first()
    return event

def query_events_ann(annotator_id, events_tbpt_ids):
    events_ann = []
    with session_scope() as session:
        events_ann = session.query(EventANN).filter(EventANN.event_id.in_(events_tbpt_ids)).filter_by(annotator_id=annotator_id).all()
        for event_ann in events_ann:
            event_ann.args_ann = session.query(ArgANN).filter_by(event_ann_id=event_ann.id, annotator_id=annotator_id).all()
    return events_ann


def get_index_by_fe_id(fe_id, args_ann):
    i = 0
    for arg_ann in args_ann:
        if fe_id ==arg_ann.event_fe_id:
            return i
        i += 1
    return None

    
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




def is_event_or_state(frame):
    if frame:
        if  is_entity(frame):
            return False
        if frame.name in ['Event', 'State']:
            return frame
        for rel_name in ['Inheritance', 'Using']:
            for rel in filter_rel(frame, rel_name):
                parcial_r = is_event_or_state(rel.Parent)
                if parcial_r:
                    return parcial_r

def is_entity(frame):
    if frame:
        if frame.name == 'Entity':
            return True
        for rel in filter_rel(frame, 'Inheritance'):
            parcial_r = is_entity(rel.Parent)
            if parcial_r:
                return parcial_r 
def is_instance(frame):
    if frame:
        if frame.name == 'Instance':
            return True
        for rel in filter_rel(frame, 'Inheritance'):
            parcial_r = is_entity(rel.Parent)
            if parcial_r:
                return parcial_r
            
def has_place_or_time(frame):
    fes_names = list(frame.FE.keys())
    return 'Place' in fes_names or 'Time' in fes_names

def is_event(frame):
    if frame and frame.name == 'Event':
        return frame
    elif frame:
        for rel_name in ['Inheritance', 'Using']:
            for rel in filter_rel(frame, rel_name):
                parcial_r = is_event(rel.Parent)
                if parcial_r:
                    return parcial_r

def is_state(frame):
    if frame and frame.name == 'State':
        return frame
    elif frame:
        for rel_name in ['Inheritance', 'Using']:
            for rel in filter_rel(frame, rel_name):
                parcial_r = is_state(rel.Parent)
                if parcial_r:
                    return parcial_r
            
def filter_inheritance(frame):
    return [rel for rel in frame.frameRelations if rel.type.name == 'Inheritance' and frame.name == rel.Child.name]


def filter_rel(frame, rel_name):
    return [rel for rel in frame.frameRelations if rel.type.name == rel_name and frame.name == rel.Child.name]


def frame_fes(frame):
    return [fe for fe in frame.FE.values()]

def filter_core_fes(frame):
    return filter_fes(frame, 'Core')

def filter_peripheral_fes(frame):
    return filter_fes(frame, 'Peripheral')

def filter_fes(frame, filter_by = 'Core'):
    return [fe for fe in frame.FE.values() if fe.coreType == filter_by]

def get_args_ann_fes(event_ann_id, annotator_id):
    fes_ann = []
    with session_scope() as session:
        args_ann = session.query(ArgANN).filter_by(event_ann_id=event_ann_id, annotator_id=annotator_id).all()
        event_ann = session.query(EventANN).filter_by(id=event_ann_id).first()
        
    args_fe_ids = [arg_ann.event_fe_id for arg_ann in args_ann]
    for fe in fn.frame(event_ann.event_fn_id).FE.values():
        if fe.ID in args_fe_ids:
            fes_ann.append(fe)
    return fes_ann
    

def get_fes_from_args(event_ann, args_ann):
    fes_ann = []
    args_fe_ids = [arg_ann.event_fe_id for arg_ann in args_ann]
    for fe in fn.frame(event_ann.event_fn_id).FE.values():
        if fe.ID in args_fe_ids:
            fes_ann.append(fe)
    return fes_ann

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


def get_all_frame_sentences(frame):
    return fn.exemplars(frame=frame)

all_frames_list = None

def get_all_event_or_state_frames(clear_cache=False):
    global all_frames_list
    if clear_cache:
        all_frames_list = []
    if not all_frames_list:
        entity_frames = all_frames(is_entity)
        place_or_time_frames = all_frames(has_place_or_time)
        event_or_state_frames =  all_frames(is_event_or_state)
        all_frames_list = [f for f in place_or_time_frames if f not in event_or_state_frames and f not in entity_frames]
        
    return all_frames_list

def get_lexunits(frame):
    return list(frame.lexUnit.keys())

def all_event_frames():
    lframes = []
    for frame in fn.frames():
        if frame:
            if not is_event(frame): continue
            lframes.append(frame)
    return lframes

def all_frames(is_filter_func=lambda f: f):
    lframes = []
    for frame in fn.frames():
        if frame:
            if not is_filter_func(frame): continue
            lframes.append(frame)
    return lframes


def fe_name_type(fe):
    return '%s <<%s>>' % (fe.name, fe.coreType)

def lemma_frames(lang='por'):
    for frame in fn.frames():
        if not is_event_or_state(frame): continue
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
                
