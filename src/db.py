import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime


import uuid


Base = declarative_base()




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
    
#     def is_span_wrong(self):
#         return self.status_span == 'wrong'

#     def is_type_wrong(self):
#         return self.status_type == 'wrong'

#     def update_status_if_not_none(self, other):
#         if other.status_span:
#             self.status_span = other.status_span
#         if other.status_type:
#             self.status_type = other.status_type
    
#     def __repr__(self):
#         return '<ValArgANN (fe_id=%s, span=%s, type=%s)>' % (self.event_fe_id, self.status_span, self.status_type)
    


