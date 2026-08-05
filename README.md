# Task Manager API

A RESTful API for managing daily tasks through standard CRUD operations,
built with **Flask** (Python) and backed by a real **SQLite database**.

## What it does

Lets you create, read, update, and delete tasks via HTTP requests. Each
task tracks a title, optional description, status (`pending` or
`completed`), and an auto-generated creation timestamp. Built to
demonstrate clean CRUD design, input validation, and proper HTTP status
codes/error handling.

## Data Model — `Task`

| Field         | Type   | Notes                                              |
|---------------|--------|-----------------------------------------------------|
| `id`          | int    | Auto-generated, unique                              |
| `title`       | string | **Required**, cannot be empty                       |
| `description` | string | Optional, defaults to `""`                          |
| `status`      | string | `"pending"` or `"completed"`, defaults to `"pending"`|
| `created_at`  | string | Auto-generated ISO 8601 UTC timestamp                |

## Requirements

- Python 3.8+
- Flask and Flask-SQLAlchemy (see `requirements.txt`)

## Setup & How to Run

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/task-manager-api.git
cd task-manager-api

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python3 app.py
```

The API will start at `http://127.0.0.1:5000`.

Storage is a **SQLite database**. A file called `tasks.db` is created
automatically in the project folder the first time you run the app —
no manual database setup or separate server required. Unlike in-memory
storage, your tasks **persist across restarts**: stop the server, start
it again, and everything you created is still there.

If you ever want to start over with a clean slate, just delete
`tasks.db` and restart the app — a fresh, empty database will be
created automatically.

## Endpoints

| Method        | Endpoint       | Description                          |
|---------------|----------------|---------------------------------------|
| `POST`        | `/tasks`       | Create a new task                     |
| `GET`         | `/tasks`       | Retrieve all tasks (optional `?status=pending`/`completed` filter) |
| `GET`         | `/tasks/<id>`  | Retrieve a specific task by ID        |
| `PUT`         | `/tasks/<id>`  | Full update of a task (title required)|
| `PATCH`       | `/tasks/<id>`  | Partial update of a task              |
| `DELETE`      | `/tasks/<id>`  | Delete a task                         |

### Example: Create a task
```bash
curl -X POST http://127.0.0.1:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```
Response — `201 Created`:
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-08-03T04:49:58.551257+00:00"
}
```

### Example: Get all tasks
```bash
curl http://127.0.0.1:5000/tasks
```

### Example: Get one task
```bash
curl http://127.0.0.1:5000/tasks/1
```

### Example: Update a task (partial)
```bash
curl -X PATCH http://127.0.0.1:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Example: Delete a task
```bash
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

## How to Run It

### macOS / Linux / Git Bash / WSL

```bash
pip install -r requirements.txt
python app.py
```

Then in another terminal:

```bash
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d '{"title":"Test task"}'
curl http://127.0.0.1:5000/tasks
```

### Windows (PowerShell)

```powershell
pip install -r requirements.txt
python app.py
```

Then in another PowerShell window:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" -Method Post -ContentType "application/json" -Body '{"title":"Test task"}'
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" -Method Get
```

> Plain `curl` in PowerShell is aliased to `Invoke-WebRequest`, which
> uses different syntax and can throw errors like
> `Cannot bind parameter 'Headers'`. Using `Invoke-RestMethod` avoids
> this entirely — see the full command reference for every endpoint
> below in **"How to Use It (Windows / PowerShell)."**

## How to Use It (Windows / PowerShell)

If you're on Windows, PowerShell aliases `curl` to its own `Invoke-WebRequest`
cmdlet, which uses different syntax than real curl and can throw confusing
errors like `Cannot bind parameter 'Headers'`. The templates below use
`Invoke-RestMethod`, PowerShell's native way to call a REST API, and avoid
that problem entirely.

Make sure the server is running first (`python app.py` or `py app.py`),
then run any of these from a **second** PowerShell window.

### Create a task — `POST /tasks`
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" -Method Post -ContentType "application/json" -Body '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

### Get all tasks — `GET /tasks`
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" -Method Get
```

### Get all tasks filtered by status — `GET /tasks?status=`
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks?status=pending" -Method Get
```

### Get a specific task by ID — `GET /tasks/<id>`
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/1" -Method Get
```

### Full update of a task — `PUT /tasks/<id>` (title required)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/1" -Method Put -ContentType "application/json" -Body '{"title": "Buy groceries and cook dinner", "description": "Milk, eggs, bread, chicken", "status": "pending"}'
```

### Partial update of a task — `PATCH /tasks/<id>`
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/1" -Method Patch -ContentType "application/json" -Body '{"status": "completed"}'
```

### Delete a task — `DELETE /tasks/<id>`
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks/1" -Method Delete
```

Replace the `1` in any ID-based command with the actual task ID you want
to target — you'll see each task's `id` in the response returned right
after you create it, or by running the `GET /tasks` command to list
everything.

**Tip:** By default, `Invoke-RestMethod` prints results as a table that
can cut off longer fields. Pipe the result to `ConvertTo-Json` to see
the full response:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/tasks" -Method Get | ConvertTo-Json
```

### macOS / Linux (real curl)

If you're not on Windows, plain `curl` works as expected:
```bash
# Create a task
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d '{"title": "Buy groceries"}'

# Get all tasks
curl http://127.0.0.1:5000/tasks

# Get one task
curl http://127.0.0.1:5000/tasks/1

# Full update
curl -X PUT http://127.0.0.1:5000/tasks/1 -H "Content-Type: application/json" -d '{"title": "Updated title", "status": "pending"}'

# Partial update
curl -X PATCH http://127.0.0.1:5000/tasks/1 -H "Content-Type: application/json" -d '{"status": "completed"}'

# Delete
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

## Validation & Error Handling

| Scenario                                   | Status Code | Response                                              |
|---------------------------------------------|-------------|--------------------------------------------------------|
| `title` missing or empty on create/PUT       | `400`       | `{"error": "'title' is required and cannot be empty."}`|
| Invalid `status` value                       | `400`       | `{"error": "'status' must be one of ['completed', 'pending']."}` |
| Request body isn't valid JSON                | `400`       | `{"error": "Request body must be valid JSON."}`        |
| Task ID doesn't exist                        | `404`       | `{"error": "Task with id <id> not found."}`             |
| Wrong HTTP method on a valid route           | `405`       | `{"error": "Method not allowed on this endpoint."}`    |
| Successful creation                          | `201`       | Full task object                                        |
| Successful read/update/delete                | `200`       | Full task object (or confirmation message for delete)  |

`PUT` requires a full replacement and enforces that `title` is present;
`PATCH` allows partial updates and only validates the fields you send.

## Testing

All endpoints were manually tested end-to-end with `curl`, covering:
- Creating tasks (valid and invalid — missing/empty title)
- Listing all tasks and filtering by status
- Fetching a single task (existing and non-existent ID → 404)
- Updating via both `PUT` (full) and `PATCH` (partial), including
  invalid status values
- Deleting a task, then confirming a second delete returns `404`

You can re-run the same checks yourself with `curl`, or import the
endpoints into **Postman**:
1. Open Postman → **Import** → paste `http://127.0.0.1:5000/tasks` as a raw request, or create requests manually for each method/endpoint above.
2. Set `Content-Type: application/json` on `POST`/`PUT`/`PATCH` requests.
3. Confirm each endpoint returns the status codes and JSON shapes described above.

## Project Structure

```
task-manager-api/
├── app.py              # Flask app: routes, DB model, validation, error handling
├── requirements.txt    # Python dependencies
├── tasks.db             # SQLite database file (auto-created on first run, not committed to git)
└── README.md           # This file
```

> `tasks.db` is created automatically the first time you run `app.py`
> and should be added to `.gitignore` so it isn't committed to GitHub
> (everyone running the project should start with their own fresh
> database).

## Possible Improvements

- Swap SQLite for PostgreSQL/MySQL for production use (only `SQLALCHEMY_DATABASE_URI` needs to change)
- Add pagination to `GET /tasks`
- Add due dates and priority levels to the task model
- Add authentication so tasks are scoped per user
