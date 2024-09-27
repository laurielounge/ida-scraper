# /models/page.py
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from models.image import Image
from models.pagelink import PageLink

Base = declarative_base()


class Page(Base):
    __tablename__ = 'scraper_page_staging'
    __table_args__ = {'schema': 'ida_audit'}

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer)
    audit_id = Column(Integer)
    url = Column(String(2048), nullable=False)
    load_time = Column(Float)
    content_type = Column(String(100))
    title = Column(String(512))
    crawl_depth = Column(Integer)
    title_length = Column(Integer)
    h1 = Column(String)
    h2 = Column(String)
    h1_count = Column(Integer)
    h2_count = Column(Integer)
    page_link_count = Column(Integer)
    broken_link_count = Column(Integer)
    image_link_count = Column(Integer)
    internal_link_count = Column(Integer)
    external_link_count = Column(Integer)
    images_without_alt_count = Column(Integer)
    status_code = Column(Integer)
    meta_description_length = Column(Integer)
    has_meta_keywords = Column(Boolean)
    is_mobile_friendly = Column(Boolean)
    has_structured_data = Column(Boolean)
    is_https = Column(Boolean)
    duplicate_content_flag = Column(Boolean)
    meta_description = Column(String)
