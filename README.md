### Документация

#### Краткое описание архитектуры системы
- **API Gateway**  
  Отвечает за маршрутизацию запросов между клиентами и микросервисами.
- **File Storing Service**  
  Принимает на вход `.txt` файлы, сохраняет их в хранилище и возвращает `file_id`.
- **File Analysis Service**  
  Принимает `file_id`, ставит задачу анализатора в очередь (Celery + Redis), сохраняет результаты в БД и возвращает статистику или информацию о дубликате.

#### Спецификация API

1. **POST /upload** (File Storing Service)  
   - **Параметры**: `file` (multipart/form-data, `.txt`)  
   - **Ответ**:
     ```json
     { "id": <int>, "message": "<string>" }
     ```

2. **GET /files/{file_id}** (File Storing Service)  
   - **Параметры**: `file_id` (path)  
   - **Ответ**: бинарный поток файла (`application/octet-stream`)

3. **POST /analyze/{file_id}** (File Analysis Service)  
   - **Параметры**: `file_id` (path)  
   - **Ответ**:
     ```json
     { "task_id": "<uuid>", "status": "PENDING" }
     ```

4. **GET /tasks/{task_id}** (File Analysis Service)  
   - **Параметры**: `task_id` (path)  
   - **Ответ** при успешном анализе:
     ```json
     {
       "task_id": "<uuid>",
       "status": "SUCCESS",
       "state": "COMPLETED",
       "result": {
         "paragraphs": <int>,
         "words": <int>,
         "characters": <int>
       }
     }
     ```
   - **Ответ** при дубликате:
     ```json
     {
       "task_id": "<uuid>",
       "status": "SUCCESS",
       "state": "DUPLICATE",
       "original_file_id": <int>
     }
     ```
   - **Ответ** при ошибке:
     ```json
     {
       "task_id": "<uuid>",
       "status": "FAILURE",
       "error": "<string>"
     }
     ```
