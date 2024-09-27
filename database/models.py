from dotenv import load_dotenv
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from database.local_db import DatabaseConnection

load_dotenv()

db = DatabaseConnection()
engine = db.get_engine()
Base = declarative_base()


class DomainData(Base):
    __tablename__ = 'domain_data'

    domain_id = Column(Integer, primary_key=True, autoincrement=True)
    domain_url = Column(String(2048), nullable=False)  # Adjusted to match schema
    total_pages = Column(Integer)
    total_images = Column(Integer)
    crawl_status = Column(String(50))  # Add to DB schema if needed
    last_crawled = Column(DateTime)  # Add to DB schema if needed

    # Relationship with PageData
    pages = relationship("PageData", back_populates="domain")


class PageData(Base):
    __tablename__ = 'page_data'

    page_id = Column(Integer, primary_key=True)
    url = Column(String(2048), nullable=False)
    load_time = Column(Float)
    content_type = Column(String(100))
    title = Column(String(512))
    crawl_depth = Column(Integer)
    title_length = Column(Integer)  # New
    h1_count = Column(Integer)
    h2_count = Column(Integer)
    page_link_count = Column(Integer)
    broken_link_count = Column(Integer)  # New
    image_link_count = Column(Integer)
    internal_link_count = Column(Integer)
    external_link_count = Column(Integer)
    images_without_alt_count = Column(Integer)  # New
    status_code = Column(Integer)
    domain_id = Column(Integer, ForeignKey('domain_data.domain_id'))
    meta_description_length = Column(Integer)  # New
    has_meta_keywords = Column(Boolean)  # New
    is_mobile_friendly = Column(Boolean)  # New
    has_structured_data = Column(Boolean)  # New
    is_https = Column(Boolean)  # New
    duplicate_content_flag = Column(Boolean)  # New

    # Relationship with DomainData
    domain = relationship("DomainData", back_populates="pages")


class ImageData(Base):
    __tablename__ = 'image_data'

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey('page_data.page_id'))
    image_url = Column(String(2048))
    alt_text = Column(String(512))
    load_time = Column(Float)
    is_internal = Column(Boolean)
    status_code = Column(Integer)
    is_broken = Column(Boolean)

    page = relationship("PageData", back_populates="images")
    # Additional fields can be added as needed


PageData.images = relationship("ImageData", order_by=ImageData.image_id, back_populates="page")


class PageLinkData(Base):
    __tablename__ = 'page_links'

    link_id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey('page_data.page_id'))
    target_url = Column(String(2048))
    is_internal = Column(Boolean)
    anchor_text = Column(String(512))
    mime_type = Column(String(100))
    is_broken = Column(Boolean)
    page = relationship("PageData", back_populates="page_links")


PageData.page_links = relationship("PageLinkData", order_by=PageLinkData.link_id, back_populates="page")


class Domain(Base):
    __tablename__ = 'domains'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_name = Column(String(255))
    scraped_at = Column(DateTime, default=datetime.now())

    pages = relationship("ScrapedPage", back_populates="domain")


class ScrapedPage(Base):
    __tablename__ = 'scraped_pages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey('domains.id'))
    url = Column(String(2048), nullable=False)
    html = Column(Text, nullable=False)
    status_code = Column(Integer)
    fetched_at = Column(DateTime, default=datetime.now())
    load_time = Column(Float)
    domain = relationship("Domain", back_populates="pages")
