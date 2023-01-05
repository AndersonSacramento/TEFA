import sqlalchemy

from sqlalchemy import Column, Integer, String, DateTime
from entities import Base


class AnnotationProject(Base):
    __tablename__  = 'annotation_project'

    name = Column(String)
    creator = relationship('Annotator', back_populates='projects')



    
