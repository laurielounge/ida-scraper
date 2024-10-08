# /routes/scraper.py
import logging
from datetime import datetime
from typing import Dict

import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crud.audit_cruds import fetch_audit_detail_from_ida, fetch_audit_from_ida, fetch_audit_detail_items_from_ida
from database.base_route import get_db
from security.secure_access import validate_api_key
# Import the Celery task
from tasks.scraper_task import run_scrapy_spider  # This is the missing import

logger = logging.getLogger("ida_audit")
router = APIRouter()


# Get all audits
@router.get("/scrape/{audit_id}", response_model=bool)
def start_scrape(audit_id: int, db: Session = Depends(get_db), user: Dict = Depends(validate_api_key)):
    ida_url = 'http://ida:8001/scraper'
    logger.info(f"Starting a scrape for website {audit_id}")

    # Fetch audit details
    audit = fetch_audit_from_ida(audit_id)
    website = audit['audit_url']
    audit_detail = fetch_audit_detail_from_ida(audit_id, website)

    audit_detail_item = fetch_audit_detail_items_from_ida(audit_detail['id'])
    if not audit_detail_item:
        logger.info("Creating a new audit detail item")
        audit_detail_item = []
        logger.error(f"No audit detail item found for {audit_detail=}")

        audit_detail_item_create = {
            'audit_detail_id': audit_detail['id'], 'query_id': 1,
            'query_start_date': datetime.now().isoformat(),
            'query_end_date': datetime.now().isoformat(),
            'status': 1, 'records_added': 0
        }

        audit_detail_item.append(requests.post(f"{ida_url}/auditdetailitem", json=audit_detail_item_create).json())

    logger.info(f"Details are {audit=} {audit_detail=} {audit_detail_item=}")

    # Dispatch the Celery task
    run_scrapy_spider.delay(audit_id, website)  # Run the Celery task
    logger.info(f"Celery task for Scrapy spider started with audit_id={audit_id} and website={website}")

    return True
