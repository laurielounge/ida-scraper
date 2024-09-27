# security/secure_access.py
import os

from dotenv import load_dotenv, find_dotenv
from fastapi import APIRouter
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader

from logging_mod.logger import logger

security = HTTPBearer()
load_dotenv(find_dotenv())

SECRET_KEY = os.getenv('JWT_SECRET_TOKEN')
IDA_API_KEY_NAME = name = os.getenv('IDA_API_KEY_NAME')
IDA_API_KEY = os.getenv('IDA_API_KEY')
router = APIRouter()
ida_api_key_header = APIKeyHeader(name=IDA_API_KEY_NAME, auto_error=True)
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def validate_api_key(api_key: str = Security(ida_api_key_header)):
    if api_key != SCRAPER_API_KEY:
        logger.error("API key is wrong")
        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"  # This is the message that will be returned if the API key is invalid
        )
    logger.info("API key is correct")
    return True  # Only reached if the API key is valid


def create_ida_header() -> dict:
    """
    Create and return the authorization header required for requests to the scraper service.

    Returns:
        A dictionary with the Authorization header containing the API key.
    """

    if not IDA_API_KEY:
        logger.error("IDA_API_KEY not found in environment variables.")
        raise EnvironmentError("IDA_API_KEY not set.")

    return {
        IDA_API_KEY_NAME: IDA_API_KEY
    }
