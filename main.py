# No CORSMiddleware warning
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logging_mod.logger import logger
from routes.scraper import router as scraper_router

origins = [
    "http://scraper",
    "http://localhost",
]
logger.info("Sparking up the app")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

logger.info('Logger initialized, app has started!')

app.include_router(scraper_router, prefix='/api')
