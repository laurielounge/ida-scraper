# /crud/scraper_cruds.py
from sqlalchemy.orm import Session
from models.domain import Domain
from models.page import Page
from models.image import Image
from models.pagelink import PageLink
from logging_mod.logger import logger


def clear_all_staging_data(db: Session, audit_id: int):
    """
    Clears all staging data related to a specific audit_id.

    Parameters:
    - db: The SQLAlchemy session.
    - audit_id: The audit ID for which the data should be cleared.
    """

    # Assuming Image and PageLink have foreign keys or logical dependencies on Page,
    # and Page has a logical dependency on Domain, start with Image and PageLink,
    # followed by Page, and finally Domain.

    # Delete Image records
    db.query(Image).filter(Image.audit_id == audit_id).delete(synchronize_session=False)

    # Delete PageLink records
    db.query(PageLink).filter(PageLink.audit_id == audit_id).delete(synchronize_session=False)

    # Delete Page records
    db.query(Page).filter(Page.audit_id == audit_id).delete(synchronize_session=False)

    # Delete Domain records
    # This assumes Domain has an audit_id and that deleting a domain won't affect other tables
    # Adjust accordingly if there are other considerations.
    db.query(Domain).filter(Domain.audit_id == audit_id).delete(synchronize_session=False)

    # Commit the changes
    db.commit()

    logger.info(f"All staging data cleared for audit_id {audit_id}")


def get_or_create_domain(db: Session, domain_name: str, audit_id: int) -> int:
    # Try to find the domain by name and audit_id
    logger.info(f"Checking for domain {domain_name} for audit_id {audit_id}")
    existing_domain = db.query(Domain).filter(Domain.domain_url == domain_name, Domain.audit_id == audit_id).first()
    if existing_domain:
        logger.info(f"Domain {domain_name} for audit_id {audit_id} already exists with ID {existing_domain.id}")
        return existing_domain.id
    else:
        # Create a new domain if it doesn't exist, using the audit_id
        new_domain = Domain(domain_url=domain_name, audit_id=audit_id)
        db.add(new_domain)
        db.commit()
        logger.info(f"New domain {domain_name} for audit_id {audit_id} created with ID {new_domain.id}")
        return new_domain.id


def get_or_create_page(db: Session, Page, **kwargs) -> int:
    # kwargs includes all necessary fields, including 'audit_id'
    existing_resource = db.query(Page).filter_by(**kwargs).first()
    if existing_resource:
        logger.info(f"Resource found with ID {existing_resource.id}")
        return existing_resource.id
    else:
        new_resource = Page(**kwargs)
        db.add(new_resource)
        db.commit()
        logger.info(f"New resource created with ID {new_resource.id}")
        return new_resource.id


def get_or_create_image(db: Session, Image, **kwargs) -> int:
    # kwargs includes all necessary fields, including 'audit_id'
    existing_resource = db.query(Image).filter_by(**kwargs).first()
    if existing_resource:
        logger.info(f"Resource found with ID {existing_resource.id}")
        return existing_resource.id
    else:
        new_resource = Image(**kwargs)
        db.add(new_resource)
        db.commit()
        logger.info(f"New resource created with ID {new_resource.id}")
        return new_resource.id


def get_or_create_pagelink(db: Session, PageLink, **kwargs) -> int:
    # kwargs includes all necessary fields, including 'audit_id'
    existing_resource = db.query(PageLink).filter_by(**kwargs).first()
    if existing_resource:
        logger.info(f"Resource found with ID {existing_resource.id}")
        return existing_resource.id
    else:
        new_resource = PageLink(**kwargs)
        db.add(new_resource)
        db.commit()
        logger.info(f"New resource created with ID {new_resource.id}")
        return new_resource.id
