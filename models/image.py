# /models/image.py
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Image(Base):
    __tablename__ = 'scraper_image_staging'
    __table_args__ = {'schema': 'ida_audit'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(Integer)
    page_id = Column(Integer)
    image_url = Column(String(2048))
    alt_text = Column(String(512))
    load_time = Column(Float)
    is_internal = Column(Boolean)
    status_code = Column(Integer)
    is_broken = Column(Boolean)
