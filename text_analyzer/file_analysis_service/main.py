import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
import uvicorn
import logging
from celery_app import celery_app
from tasks import analyze_file
from db import init_db, get_result_by_file_id

app = FastAPI(title="File Analysis Service (with Celery)")

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/analyze/{file_id}", summary="Запустить анализ файла (асинхронно)")
async def analyze_endpoint(file_id: int):
    # Ставим задачу в очередь и возвращаем task_id
    task = analyze_file.delay(file_id)
    return {"task_id": task.id, "status": task.status}

@app.get("/tasks/{task_id}", summary="Статус и результат задачи анализа")
async def get_task_status(task_id: str):
    """
    Возвращает текущее состояние задачи и, если готово, результат.
    """
    try:
        res = AsyncResult(task_id)    # используем default app
        response = {"task_id": task_id, "status": res.status}

        if res.status == "SUCCESS":
            result = res.result  
            if isinstance(result, dict):
                response.update(result)
            else:
                response["result"] = str(result)

        elif res.status in ("FAILURE", "REVOKED"):
            response["error"] = str(res.result)

        return JSONResponse(response)

    except Exception as e:
        logging.exception("Error in get_task_status")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


if __name__ == "__main__":
    uvicorn.run("file_analysis_service.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8001)))
