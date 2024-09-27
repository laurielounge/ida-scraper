from database.db_connections import DatabaseConnections
from crud.audit_cruds import fetch_audit_from_ida, fetch_audit_detail_from_ida, fetch_audit_detail_items_from_ida, \
    update_first_audit_detail_item
from logging_mod import logger
import pandas as pd
from models.domain import Domain
from models.page import Page

database_connections = DatabaseConnections()

# Use the appropriate session for your schema. Here, using the audit schema as an example.
db_session = database_connections.get_audit_session()
engine = database_connections.audit_engine
audit_id = 30
audit = fetch_audit_from_ida(audit_id)
website = audit['audit_url']
audit_detail = fetch_audit_detail_from_ida(audit_id, website)
audit_detail_items = fetch_audit_detail_items_from_ida(audit_detail['id'])
print(audit_detail_items)
result = db_session.query(Domain).all()
print(result)

worked = update_first_audit_detail_item(audit_id=30, records_updated=200)

try:
    # Assuming domain_id is obtained or generated beforehand
    domain_id = 7
    domain = db_session.query(Domain).filter_by(id=domain_id).first()
    if not domain:
        # Handle the case where the domain does not exist
        print(f"Domain with id {domain_id} does not exist.")
    else:
        # Proceed to save the Page, referencing the existing Domain
        page = Page(domain_id=domain.id, url="http://www.mimeanalytics.com")
        db_session.add(page)
        db_session.commit()
except Exception as e:
    db_session.rollback()
    # Log or handle the exception
    print(f"Error during saving: {e}")
finally:
    db_session.close()
