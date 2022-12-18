import sqlalchemy


from sqlalchemy import Column, Integer, String, DateTime


class EventFrameElement(Base):
    __tablename__ = 'event_fe'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)
    frame_id = Column(Integer, ForeignKey('event_fn.id'))

    event_fn = relationship("EventFN", back_populates="fes")
