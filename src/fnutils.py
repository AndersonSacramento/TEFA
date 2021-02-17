from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
import sqlalchemy
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

import timebankpttoolkit.timebankptcorpus as timebankpt
from datetime import datetime, timezone
import uuid

from db import SentenceAnnotator, Annotator, LemmaFN, EventTBPT, TimeExpTBPT, Sentence, engine

def create_session():
    global Session
    Session = sessionmaker(bind=engine)

def now():
    return datetime.now(timezone.utc)

def create_annotator(email):
    session = Session()
    annotator = Annotator(email=email, created_at=now())
    session.add(annotator)
    session.commit()
    create_all_sentence_annotator(annotator)
    return annotator

def create_all_sentence_annotator(annotator):
    session = Session()
    for sentence in session.query(Sentence).all():
        session.add(SentenceAnnotator(annotator_id=annotator.email,
                                      sentence_id=sentence.id,
                                      status='todo'))
    session.commit()
    
def get_all_annotators():
    session = Session()
    return session.query(Annotator).all()
    
def query_lemma(lemma_name):
    session = Session()
    return session.query(LemmaFN).filter_by(lemma=lemma_name).all()

def query_frameid(lemma_name):
    session = Session()
    return {out[0] for out in session.query(LemmaFN.frameid).filter_by(lemma=lemma_name).all()}


def load_sentences(annotator_id, status):
    session = Session()
    sentences = session.query(Sentence).\
                   join(SentenceAnnotator, Sentence.id==SentenceAnnotator.sentence_id).\
                   join(Annotator, Annotator.email==SentenceAnnotator.annotator_id).\
                   filter(SentenceAnnotator.status==status,
                          SentenceAnnotator.annotator_id==annotator_id).\
                   all()
    #session.commit()
    return sentences
    
def change_sentence_status(sentence, email, status):
    session = Session()
    sentence_annotator = session.query(SentenceAnnotator).filter_by(annotator_id=email, sentence_id=sentence.id).first()
    if sentence_annotator:
        sentence_annotator.status = status
    print(sentence_annotator)
    session.commit()

    
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
                
