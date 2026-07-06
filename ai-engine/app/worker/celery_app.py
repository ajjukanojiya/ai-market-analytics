from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"]
)

celery_app.conf.task_routes = {
    "app.worker.tasks.*": {"queue": "main-queue"}
}

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    "fetch-nifty-5m-data": {
        "task": "fetch_nifty_live_data",
        "schedule": 300.0, # Every 5 minutes (300 seconds)
    }
}
celery_app.conf.timezone = "Asia/Kolkata"
