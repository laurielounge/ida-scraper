import redis
from fastapi import APIRouter

from celery_app import celery_app
from logging_mod.logger import logger
from tasks.scraper_task import redis_ping_task, hello_world,example_task

router = APIRouter()


@router.get("/redis-test")
def test_redis():
    r = redis.Redis(host='localhost', port=6379)
    if r.ping():
        return {"status": "Redis connection successful"}
    return {"status": "Redis connection failed"}


# @router.get("/redis-celery")
# def test_redis_via_celery():
#     task = redis_ping_task.delay()  # Dispatch the Celery task
#     return {"status": "Task dispatched"}

@router.get("/rabbitmq-celery")
def test_rabbitmq_via_celery():
    try:
        task = example_task.delay()
        return {"status": "Task dispatched", "task_id": task.id}
    except Exception as e:
        return {"error": str(e)}

@router.get("/redis-celery")
def test_redis_via_celery():
    try:
        # Log the broker URL for debugging
        logger.info(f"Broker URL in FastAPI: {celery_app.conf.broker_url}")
        task = redis_ping_task.delay()
        return {"status": "Task dispatched", "task_id": task.id}
    except Exception as e:
        return {"error": str(e)}


@router.get("/celery-status")
def test_celery_connection():
    try:
        broker_alive = celery_app.control.inspect().ping()
        registrations = celery_app.control.inspect().registered()
        if broker_alive:
            return {"status": f"Celery is connected, {registrations=}"}
        else:
            return {"status": "Celery is not responding"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}


@router.get("/hello-world")
def hello_world_connection():
    try:
        logger.info(f"Broker URL: {celery_app.conf.broker_url}")
        task = hello_world.delay()
        logger.debug(f"Success")
        return {"status": "Task dispatched", "task_id": task.id}
    except Exception as e:
        logger.error(f"Error dispatching Celery task: {e}")
        return {"status": "Error", "details": str(e)}
