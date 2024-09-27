from datetime import datetime

import requests

from logging_mod.logger import logger
from security.secure_access import create_ida_header


def fetch_audit_from_ida(audit_id: int):
    logger.info("Asking for audit details")
    headers = create_ida_header()  # Ensure this function returns the correct headers for ida
    logger.info(f"Header {headers=}")
    ida_url = f"http://ida:8001/scraper/audits/{audit_id}"
    response = requests.get(ida_url, headers=headers)
    logger.info(f"Response {response=}")
    if response.status_code == 200:
        return response.json()  # Assuming the endpoint returns JSON with audit details
    else:
        logger.error(
            f"Failed to fetch audit details from ida for audit_id={audit_id}, Status Code={response.status_code}")
        # Handle error or fallback
        return None


def fetch_audit_detail_from_ida(audit_id: int, website: str):
    """ Only want the one record for api 13. If there isn't one, create it"""
    logger.info("Asking for audit details")
    headers = create_ida_header()  # Ensure this function returns the correct headers for ida
    ida_url = f"http://ida:8001/scraper/audits/auditdetails/{audit_id}"
    response = requests.get(ida_url, headers=headers)
    details = response.json()
    logger.info(f"Response {details=}")
    matching_audit_detail = next((detail for detail in details if detail['api_id'] == 13), None)

    if matching_audit_detail:
        return matching_audit_detail
    else:
        return create_audit_detail(audit_id, website)


def create_audit_detail(audit_id, website):
    logger.info("Creating audit details")
    audit_detail = {'audit_id': audit_id, 'api_id': 13, 'api_identifier': website, 'status': 2, 'status_message': None,
                    'error_message': None, 'last_updated': datetime.now().isoformat(),
                    'start_date': datetime.now().date().isoformat(), 'end_date': None, 'reload_data': False}
    headers = create_ida_header()
    ida_url = "http://ida:8001/scraper/auditdetails"
    response = requests.post(ida_url, json=audit_detail, headers=headers)  # Include audit_detail as JSON

    if response.status_code == 200:
        # Process successful creation/find response
        logger.info("Audit detail created or found successfully.")
        return response.json()  # Assuming response contains useful data
    else:
        # Handle errors
        logger.error(f"Failed to create/find audit detail. Status Code: {response.status_code}")
        return None


def update_audit_detail(audit_detail_update: dict):
    logger.info("Updating audit detail")
    audit_detail_id = audit_detail_update['audit_detail_id']
    headers = create_ida_header()
    ida_url = f"http://ida:8001/scraper/auditdetails/{audit_detail_id}"
    response = requests.put(ida_url, json=audit_detail_update, headers=headers)

    # Check response status and handle errors
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to update audit detail. Status Code: {response.status_code}")
        return None


def update_first_audit_detail_item(audit_id: int, records_updated: int):
    headers = create_ida_header()
    ida_url = f"http://ida:8001/scraper/auditdetailupdate/{audit_id}?records_updated={records_updated}"
    response = requests.put(ida_url, headers=headers)

    # Check response status and handle errors
    if response.status_code == 200:
        return True
    else:
        logger.error(f"Failed to update audit detail. Status Code: {response.status_code}")
        return None


def update_audit_detail_item(audit_detaiL_item_update: dict):
    logger.info("Updating audit detail item")
    audit_detail_item_id = audit_detaiL_item_update['audit_detail_item_id']
    headers = create_ida_header()
    ida_url = f"http://ida:8001/scraper/auditdetailitems/{audit_detail_item_id}"
    response = requests.put(ida_url, json=audit_detaiL_item_update, headers=headers)

    # Check response status and handle errors
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to update audit detail item. Status Code: {response.status_code}")
        return None


def update_audit_items_by_audit_id(audit_id):
    logger.info("Updating audit detail item from the audit_id")
    audit = fetch_audit_from_ida(audit_id)
    audit_detail = fetch_audit_detail_from_ida(audit_id, audit['website_url'])
    audit_detail_item_id = audit_detaiL_item_update['audit_detail_item_id']
    headers = create_ida_header()
    ida_url = f"http://ida:8001/scraper/auditdetailitems/{audit_detail_item_id}"
    response = requests.put(ida_url, json=audit_detaiL_item_update, headers=headers)

    # Check response status and handle errors
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to update audit detail item. Status Code: {response.status_code}")
        return None


def create_audit_detail_item(audit_detail_id):
    logger.info("Creating audit detail item")
    audit_detail_item = {'audit_detail_id': audit_detail_id, 'query_id': 1, 'status': 1,
                         'query_start_date': datetime.now().date().isoformat(), 'records_added': 0
                         }
    headers = create_ida_header()
    ida_url = "http://ida:8001/scraper/auditdetailitem"
    response = requests.post(ida_url, json=audit_detail_item, headers=headers)  # Include audit_detail as JSON

    if response.status_code == 200:
        # Process successful creation/find response
        logger.info("Audit detail item created or found successfully.")
        return response.json()  # Assuming response contains useful data
    else:
        # Handle errors
        logger.error(f"Failed to create/find audit detail item. Status Code: {response.status_code}")
        return None


def fetch_audit_detail_items_from_ida(audit_detail_id: int):
    logger.info("Asking for audit detail items")
    headers = create_ida_header()  # Ensure this function returns the correct headers for ida
    ida_url = f"http://ida:8001/scraper/auditdetailitems/{audit_detail_id}"
    response = requests.get(ida_url, headers=headers)

    if response.status_code == 200:
        audit_detail_item = response.json()
        if not audit_detail_item:
            audit_detail_item = create_audit_detail_item(audit_detail_id)
        return audit_detail_item  # Assuming the endpoint returns JSON with audit details
    else:
        logger.error(
            f"Failed to fetch audit detail items from ida for audit_detail_id={audit_detail_id}, Status Code={response.status_code}")
        # Handle error or fallback
        return None
