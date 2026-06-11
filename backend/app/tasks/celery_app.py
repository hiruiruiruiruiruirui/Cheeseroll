"""Celery application configuration."""

from celery import Celery

from ..config import settings

celery_app = Celery(
    "study_assistant",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_soft_time_limit=120,
    task_time_limit=180,
)

# Import tasks so Celery auto-discovers them
from . import process_task  # noqa
