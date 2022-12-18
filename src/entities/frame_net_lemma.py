import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime


Base = declarative_base()


class FrameNetLemma(Base):
    __tablename__ = 'frame_net_lemma'

    lexunitid = Column(Integer, primary_key=True)
    lemma = Column(String, primary_key=True)
    pos = Column(String)
    frameid = Column(Integer, primary_key=True)
    lang = Column(String)

    def __repr__(self):
        return '<FrameNetLemma (lexunitid=%s, lemma=%s, pos=%s)>' % (self.lexunitid, self.lemma, self.pos)


    def copy(self):
        return FrameNetLemma(lexunitid=self.lexunitid,
                       lemma=self.lemma,
                       pos=self.pos,
                       frameid=self.frameid,
                       lang=self.lang)

