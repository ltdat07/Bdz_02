import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

from db import init_db, insert_file, get_file_by_hash, get_file_by_id
from storage import compute_hash, save_file, load_file

app = FastAPI(title="File Storing Service")

# При старте создаём таблицы, если их нет
@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/upload", summary="Загрузить файл", response_model=dict)
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    file_hash = compute_hash(content)

    # Если файл с таким хэшем уже есть — возвращаем существующий ID
    existing = get_file_by_hash(file_hash)
    if existing:
        return {"id": existing.id, "message": "File already exists"}

    # Иначе сохраняем содержимое и метаданные
    location = save_file(content, file.filename)
    record = insert_file(name=file.filename, file_hash=file_hash, location=location)
    return {"id": record.id, "message": "File uploaded successfully"}


@app.get("/files/{file_id}", summary="Скачать файл")
def download(file_id: int):
    # Ищем метаданные
    metadata = get_file_by_id(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")

    # Читаем содержимое и отдаем стримом
    data = load_file(metadata.location)
    return StreamingResponse(
        iter([data]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={metadata.name}"}
    )


if __name__ == "__main__":
    uvicorn.run("file_storing_service.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
