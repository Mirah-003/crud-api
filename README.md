# Task API

A lightweight RESTful CRUD API for managing to-do tasks, built with Python, FastAPI, and Pydantic.

## How to run it

1. **Clone this repo**
   ```bash
   git clone https://github.com/hafsat-abdulhamid/crud-api.git
   cd crud-api
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate virtual environment**
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be running at `http://localhost:8000`.

## Endpoints

| Method | Path | Description | Status codes |
|---|---|---|---|
| `GET` | `/` | API info | `200` |
| `GET` | `/health` | Health check | `200` |
| `GET` | `/tasks` | List all tasks | `200` |
| `GET` | `/tasks/{id}` | Get one task | `200`, `404` |
| `POST` | `/tasks` | Create a task | `201`, `400` |
| `PUT` | `/tasks/{id}` | Update a task | `200`, `400`, `404` |
| `DELETE` | `/tasks/{id}` | Delete a task | `204`, `404` |

## Example curl output

```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
date: Mon, 03 Aug 2026 20:02:10 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

Interactive documentation is available at `http://localhost:8000/docs` while the server is running:

![Swagger UI](swagger.png)
