import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

from config import Config

# Use MySQL as broker and backend to avoid Redis dependency on Windows
celery_app = Celery("acd_tasks", broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND, include=["tasks"])

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
