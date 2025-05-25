from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

from .storage import save_file_to_storage, get_file_from_storage
from .db import init_db, get_file_metadata, insert_file_metadata
from .models import FileMetadata

app = FastAPI(
    title="File Storing Service",
    description="Сервис для загрузки и выдачи файлов",
    version="1.0.0"
)

# Инициализация подключения к БД
@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/upload", response_model=FileMetadata)
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    # Вычисление хэша внутри insert_file_metadata
    try:
        metadata = insert_file_metadata(filename=file.filename, content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Сохраняем файл в сторадж по полученному location
    try:
        save_file_to_storage(location=metadata.location, content=content)
    except Exception as e:
        # В случае ошибки можно откатить запись метаданных
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {e}")

    return metadata


@app.get("/files/{file_id}")
async def download_file(file_id: int):
    # Получаем метаданные файла из БД
    metadata = get_file_metadata(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Файл не найден")

    # Получаем содержимое из стораджа
    try:
        content = get_file_from_storage(location=metadata.location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла из стораджа: {e}")

    # Отдаем бинарный поток пользователю
    return StreamingResponse(
        content=iter([content]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=\"{metadata.name}\""}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
