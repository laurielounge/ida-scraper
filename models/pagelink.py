# /models/pagelink.py
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PageLink(Base):
    __tablename__ = 'scraper_pagelink_staging'
    __table_args__ = {'schema': 'ida_audit'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(Integer)
    page_id = Column(Integer)
    target_url = Column(String(2048))
    is_internal = Column(Boolean)
    anchor_text = Column(String(512))
    mime_type = Column(String(100))
    is_broken = Column(Boolean)
