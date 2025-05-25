from celery import Celery
import os

broker = os.getenv("CELERY_BROKER_URL")
backend = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "file_analysis_service",
    broker=broker,
    backend=backend,
    include=["tasks"],      # <— вот это добавлено
)

# Для полной совместимости можно:
app = celery_app
