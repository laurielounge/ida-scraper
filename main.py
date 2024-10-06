# No CORSMiddleware warning
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from logging_mod.logger import logger
from routes.scraper import router as scraper_router
from routes.redis_route import router as redis_router

origins = [
    "http://scraper",
    "http://localhost",
]
logger.info("Sparking up the app from main.py")
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
app.include_router(redis_router, prefix='/api')


@app.middleware("http")
async def log_request(request: Request, call_next):
    logger.debug("Here's what the middleware says:")
    logger.debug(f"Request URL: {request.url}")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request headers: {request.headers}")

    # Read and log the request body
    body = await request.body()
    logger.debug(f"Request body: {body.decode('utf-8')}")

    response = await call_next(request)
    return response