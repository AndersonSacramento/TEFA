import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from nltk.corpus import framenet as fn
import sys
import glob
import uuid
import timebankpttoolkit.timebankptcorpus as timebankpt
from concrete.util import read_communication_from_file, lun, get_tokens
from datetime import datetime, timezone

engine = create_engine('sqlite:///lome_tbpt.db',  connect_args={'check_same_thread': False}, echo=False)

Base = declarative_base()



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

def now():
    return datetime.now(timezone.utc)

def str_uuid():
    return str(uuid.uuid4())


def create_session():
    global Session
    Session = sessionmaker(bind=engine, expire_on_commit=False)


class SituationLome(Base):
    __tablename__ = 'situation_lome'

    id = Column(String, primary_key=True)
    frame_id = Column(Integer)
    text = Column(String)
    start_at = Column(Integer)
    end_at = Column(Integer)

    sentence_id = Column(String, ForeignKey('sentence.id'))
    arguments = relationship('ArgumentLome', back_populates='situation')

class ArgumentLome(Base):
    __tablename__ = 'argument_lome'

    id = Column(String, primary_key=True)
    text = Column(String)
    fe_id = Column(Integer)
    start_at = Column(Integer)
    end_at = Column(Integer)
    situation_id = Column(String, ForeignKey('situation_lome.id'), primary_key=True)
    sentence_id = Column(String, ForeignKey('sentence.id'), primary_key=True)
    situation = relationship('SituationLome', back_populates='arguments')


class Sentence(Base):
    __tablename__ = 'sentence'

    id = Column(String, primary_key=True)
    text = Column(String)
    document_name = Column(String)
    position = Column(Integer)
    events = relationship('EventTBPT', back_populates='sentence')

    
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



# class ValEventANN(Base):
#     __tablename__ = 'val_event_ann'

#     event_ann_id = Column(String, ForeignKey('event_ann.id'), primary_key=True)
#     annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
#     status_type = Column(String)

#     def is_wrong(self):
#         return self.status_type == 'wrong'
    
# class ValArgANN(Base):
#     __tablename__ = 'val_arg_ann'

#     event_ann_id = Column(String, ForeignKey('event_ann.id'), primary_key=True)
#     annotator_id = Column(String, ForeignKey('annotator.email'), primary_key=True)
#     event_fe_id = Column(String, ForeignKey('arg_ann.event_fe_id'), primary_key=True)
#     status_span = Column(String)
#     status_type = Column(String)
    

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

def get_all_annotators():
    annotators = []
    with session_scope() as session:
        annotators = session.query(Annotator).all()
    return annotators

def create_annotator(email):
    with session_scope() as session:
        annotator = Annotator(email=email, created_at=now())
        session.add(annotator)
        create_all_sentence_annotator(annotator)
    return annotator


def create_all_sentence_annotator(annotator):
    with session_scope() as session:
        for sentence in session.query(Sentence).all():
            session.add(SentenceAnnotator(annotator_id=annotator.email,
                                          sentence_id=sentence.id,
                                          status='todo'))


def load_all_lome_event_ann():
    with session_scope() as session:
        for (situation, event) in query_lome_event_matches():
            event_ann = EventANN(id=str_uuid(),
                                 event_id=event.id,
                                 event_fn_id=situation.frame_id,
                                 created_at=now(),
                                 updated_at=now(),
                                 annotator_id='lome')
            session.add(event_ann)
            for arg_lome in query_args_lome(situation.id):
                session.add(ArgANN(start_at=arg_lome.start_at,
                                   end_at=arg_lome.end_at,
                                   created_at=now(),
                                   event_fe_id=arg_lome.fe_id,
                                   event_ann_id=event_ann.id,
                                   annotator_id='lome'))



def query_args_lome(situation_id):
    args_lome = []
    with session_scope() as session:
        args_lome = session.query(ArgumentLome).\
            filter_by(situation_id=situation_id).all()
    return args_lome
    
def query_lome_event_matches():
    situations_events = []
    with session_scope() as session:
        situations_events = session.query(SituationLome, EventTBPT).\
            filter(SituationLome.sentence_id==EventTBPT.sentence_id).\
            filter(SituationLome.end_at==EventTBPT.end_at,
                   SituationLome.start_at==EventTBPT.start_at,
                   SituationLome.text==EventTBPT.trigger).\
                all()
    return situations_events
    

def query_sentence(doc_name, sent_text, session):
    return session.query(Sentence).filter_by(document_name=doc_name,
                                             text=sent_text).first()                         
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
            session.commit()

            
def print_entity_and_mentions(comm):
    for entitySet in lun(comm.entitySetList):
        for ei, entity in enumerate(entitySet.entityList):
            print('Entity %s (%s)' % (ei, entity.canonicalName))
            for i, mention in enumerate(entity.mentionList):
                print('  Mention %s: %s' % (i, mention.text))
            print('')
        print('')


def get_sentence_text(sentence):
    return ' '.join([token.text for token in get_tokens(sentence.tokenization)])

def get_situation_mentions(comm, situation_type='EVENT'):
    situation_type_dict = {}
    for i, situation_mention_set in enumerate(comm.situationMentionSetList):
        types = list({situation_mention.situationType for situation_mention in situation_mention_set.mentionList})
        situation_type_dict[types[0]] = situation_mention_set.mentionList
    return situation_type_dict.get(situation_type, [])

def get_mention_tokens(mention):
    return [token.text for token in mention.tokens.tokenization.tokenList.tokenList]

def get_mention_full_text(mention):
    return ' '.join(get_mention_tokens(mention))

def get_args_from_situation(situation):
    return [(arg.entityMentionId.uuidString, arg.entityMention.text, arg.role, get_mention_start_end(arg.entityMention)) for arg in lun(situation.argumentList)]



def get_all_comm_in(dir_path):
    return glob.glob('%s*.comm' % dir_path)


def get_mention_text(mention):
    token_indices = mention.tokens.tokenIndexList
    tokens = [mention.tokens.tokenization.tokenList.tokenList[token_index].text for token_index in token_indices]

    return without_final_punk(' '.join(tokens))

def get_mention_start_end(mention):
    token_indices = mention.tokens.tokenIndexList
    mention_text = get_mention_text(mention)
    text_before_mention = ' '.join([mention.tokens.tokenization.tokenList.tokenList[token_index].text for token_index in range(token_indices[0])])
    start_at = len(text_before_mention) + 1 if len(text_before_mention) > 0 else 0
    end_at = start_at + len(mention_text)

    return start_at, end_at



def query_situation_mentions(id, session):
    return session.query(SituationLome).filter_by(id=id).first()

def query_situation_mentions(session):
    return session.query(SituationLome).all()


def update_all_argument_text():
    session = Session()
    for arg in session.query(ArgumentLome).all():
        arg.text = without_final_punk(arg.text)
        arg.end_at += 1
    session.commit()
    
def update_all_situations_text():
    session = Session()
    for smention in query_situation_mentions(session):
        smention.text = without_final_punk(smention.text)
        smention.end_at -= 1
    session.commit()
        
def without_final_punk(text):
    return text[:-1] if text.endswith('.') or text.endswith(',') else text
    
def persist_events_from_comm(dir_path):
    session = Session()
    i = 1
    for comm_filename in get_all_comm_in(dir_path):
        comm = read_communication_from_file(comm_filename)
        document_name = comm.id.split('.comm')[0]
        print('Nº %s \t, Doc: %s' % (i, document_name))
        i += 1
        for smention in get_situation_mentions(comm, situation_type='EVENT'):
            situation_fn_type = smention.situationKind
            situation_start, situation_end = get_mention_start_end(smention)
            sentence = query_sentence(document_name, get_mention_full_text(smention), session)
            situation_text = without_final_punk(smention.text)
            if sentence:
                frame = fn.frame(situation_fn_type)
                try:
                    session.add(SituationLome(id=smention.uuid.uuidString,
                                frame_id=frame.ID,
                                text=situation_text,
                                start_at=situation_start,
                                end_at=situation_end,
                                sentence_id=sentence.id ))
                    session.commit()
                except sqlalchemy.exc.IntegrityError:
                    session.rollback()
                    continue
                for (arg_id, arg_text, arg_role, (arg_start, arg_end)) in get_args_from_situation(smention):
                    fe = frame.FE.get(arg_role)
                    arg_text = without_final_punk(arg_text)
                    try:
                        session.add(ArgumentLome(id=arg_id,
                                             text=arg_text,
                                             fe_id=fe.ID,
                                             start_at=arg_start,
                                             end_at=arg_end,
                                             situation_id=smention.uuid.uuidString,
                                             sentence_id=sentence.id))
                        session.commit()
                    except sqlalchemy.exc.IntegrityError:
                        session.rollback()
                        continue
    session.close()
                


# if __name__ == '__main__':

#     if len(sys.argv) > 1:
#         filepath = sys.argv[1]
#     else:
#         filepath = '../data/output-aida/wsj_0135.comm'
        
#     comm = read_communication_from_file(filepath)
