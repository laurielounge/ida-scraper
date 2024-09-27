# /models/domain.py
from sqlalchemy import Column, String, Integer, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from models.page import Page

Base = declarative_base()


class Domain(Base):
    __tablename__ = 'scraper_domain_staging'
    __table_args__ = {'schema': 'ida_audit'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    audit_id = Column(BigInteger)
    domain_url = Column(String(2048), nullable=False)
    total_pages = Column(Integer)
    total_images = Column(Integer)
    crawl_status = Column(String(50))
    last_crawled = Column(DateTime)
