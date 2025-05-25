import os
import httpx
from celery import shared_task
from analyzer import compute_text_hash, analyze_text
from db import insert_result, get_result_by_text_hash, get_result_by_file_id
from sqlalchemy.exc import IntegrityError

FILE_STORAGE_URL = os.getenv("FILE_STORAGE_URL", "http://file_storage_app:8000")

@shared_task(bind=True, name="file_analysis_service.analyze_file")
def analyze_file(self, file_id: int):
    file_url = f"{FILE_STORAGE_URL}/files/{file_id}"
    try:
        resp = httpx.get(file_url, timeout=10.0)
    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)

    if resp.status_code == 404:
        return {"state": "FAILURE", "reason": "File not found"}
    if resp.status_code != 200:
        raise self.retry(countdown=5, max_retries=3)

    # Декодируем содержимое
    try:
        text = resp.content.decode('utf-8')
    except UnicodeDecodeError:
        return {"state": "FAILURE", "reason": "Unsupported file encoding"}

    # Проверяем дубликаты
    txt_hash = compute_text_hash(text)
    dup = get_result_by_text_hash(txt_hash)
    if dup:
        return {"state": "DUPLICATE", "original_file_id": dup.file_id}

    # Анализируем статистику
    stats = analyze_text(text)

    # Сохраняем результат
    result = insert_result(
        file_id=file_id,
        text_hash=txt_hash,
        paragraphs=stats["paragraphs"],
        words=stats["words"],
        characters=stats["characters"],
        extra={}
    )

    return {"state": "COMPLETED", "result": stats}

