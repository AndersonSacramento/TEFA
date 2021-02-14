import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String

import uuid

engine = create_engine('sqlite:///tefa.db', echo=True)
Base = declarative_base()


class TriggerLemma(Base):
    __tablename__ = 'triggers_lemma'

    lexunitid = Column(Integer, primary_key=True)
    lemma = Column(String)
    pos = Column(String)
    frameid = Column(Integer)
    lang = Column(String)


class EventFN(Base):
    __tablename__ = 'event_fn'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)


class EventFE(Base):
    __tablename__ = 'event_fe'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)
    frame_id = Column(Integer, ForeignKey('event_fn.id'))

    event_fn = relationship("EventFN", back_populates="fes")


class Sentence(Base):
    __tablename__ = 'sentence'

    id = Column(Integer, primary_key=True)
    text = Column(String)

class EventTBPT(Base):
    __tablename__ = 'event_tbpt'

    id = Column(String, primary_key=True)
    trigger = Column(String)
    lemma = Column(String)
    pos = Column(String)
    start_at = Column(Integer)
    end_at = Column(Integer)

    sentence_id = Column(Integer, ForeignKey('sentence.id'))
    sentence = relationship('Sentence', back_populates='events')
    
class TimeExpressionTBPT(Base):
    __tablename__ = 'time_expression_tbpt'

    id = Column(String, primary_key=True)
    text = Column(String)
    

def create_tables_srl_events(c):
    c.execute('''CREATE TABLE IF NOT EXISTS sentence(
    id integer primary key autoincrement,
    sentence text unique )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS event_sentence(
    id integer primary key autoincrement,
    trigger text,
    sentenceid integer,
    FOREIGN KEY(sentenceid) REFERENCES sentence(id))''')
    # missing the position the event in the sentence

    
    c.execute('''CREATE TABLE IF NOT EXISTS srl_predicate(
    id integer primary key autoincrement,
    predicate text,
    sentenceid integer,
    FOREIGN KEY(sentenceid) REFERENCES sentence(id)) ''')

    c.execute('''CREATE TABLE IF NOT EXISTS verbnetbr_class(
    class text unique)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS event_verbnetbr_class(
    classid text,
    eventid integer,
    FOREIGN KEY(classid) REFERENCES verbnetbr_class(class),
    FOREIGN KEY(eventid) REFERENCES event_sentence(id))''')


    
def load_verbnetbr_class():
    conn = sqlite3.connect('timebankpt.db')
    c = conn.cursor()
    create_tables_srl_events(conn)
    conn.commit()
    conn.close()
