"""
app.py — Task Manager API

A simple RESTful CRUD API for managing tasks, built with Flask.

Data model (Task):
    id           - int, auto-generated, unique
    title        - string, required, cannot be empty
    description  - string, optional
    status       - string, "pending" or "completed" (defaults to "pending")
    created_at   - ISO 8601 timestamp, auto-generated

Storage:
    Tasks are kept in memory in a Python dict (`tasks_db`), keyed by id.
    This keeps the project dependency-free and easy to run/grade, but
    means data resets every time the server restarts. Swapping in a
    real database (SQLite/Postgres) later would only require changing
    the functions in this file that touch `tasks_db` — the route logic
    and validation would stay the same.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timezone
from itertools import count

app = Flask(__name__)

# --- In-memory "database" ---
tasks_db = {}
id_counter = count(1)  # generates 1, 2, 3, ... for new task ids

VALID_STATUSES = {"pending", "completed"}


def error_response(message, status_code):
    """Uniform JSON error shape for every failure case."""
    return jsonify({"error": message}), status_code


def serialize_task(task):
    """Return the task dict as-is (kept as a function so the JSON shape
    is defined in exactly one place, in case fields change later)."""
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "created_at": task["created_at"],
    }


# ---------------------------------------------------------------------
# POST /tasks — Create a new task
# ---------------------------------------------------------------------
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Request body must be valid JSON.", 400)

    title = data.get("title")
    if not title or not str(title).strip():
        return error_response("'title' is required and cannot be empty.", 400)

    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        return error_response(
            f"'status' must be one of {sorted(VALID_STATUSES)}.", 400
        )

    task_id = next(id_counter)
    task = {
        "id": task_id,
        "title": str(title).strip(),
        "description": data.get("description", "") or "",
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    tasks_db[task_id] = task

    return jsonify(serialize_task(task)), 201


# ---------------------------------------------------------------------
# GET /tasks — Retrieve all tasks (optionally filter by ?status=)
# ---------------------------------------------------------------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    status_filter = request.args.get("status")
    if status_filter and status_filter not in VALID_STATUSES:
        return error_response(
            f"'status' filter must be one of {sorted(VALID_STATUSES)}.", 400
        )

    tasks = list(tasks_db.values())
    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    return jsonify([serialize_task(t) for t in tasks]), 200


# ---------------------------------------------------------------------
# GET /tasks/<id> — Retrieve a specific task
# ---------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = tasks_db.get(task_id)
    if task is None:
        return error_response(f"Task with id {task_id} not found.", 404)
    return jsonify(serialize_task(task)), 200


# ---------------------------------------------------------------------
# PUT/PATCH /tasks/<id> — Update an existing task
# ---------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["PUT", "PATCH"])
def update_task(task_id):
    task = tasks_db.get(task_id)
    if task is None:
        return error_response(f"Task with id {task_id} not found.", 404)

    data = request.get_json(silent=True)
    if data is None:
        return error_response("Request body must be valid JSON.", 400)

    # PUT expects a full replacement (title required); PATCH is partial.
    if request.method == "PUT":
        if "title" not in data or not str(data.get("title", "")).strip():
            return error_response(
                "'title' is required and cannot be empty for a full update (PUT).",
                400,
            )

    if "title" in data:
        if not str(data["title"]).strip():
            return error_response("'title' cannot be empty.", 400)
        task["title"] = str(data["title"]).strip()

    if "description" in data:
        task["description"] = data["description"] or ""

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return error_response(
                f"'status' must be one of {sorted(VALID_STATUSES)}.", 400
            )
        task["status"] = data["status"]

    return jsonify(serialize_task(task)), 200


# ---------------------------------------------------------------------
# DELETE /tasks/<id> — Remove a task
# ---------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = tasks_db.get(task_id)
    if task is None:
        return error_response(f"Task with id {task_id} not found.", 404)

    del tasks_db[task_id]
    return jsonify({"message": f"Task with id {task_id} deleted successfully."}), 200


# ---------------------------------------------------------------------
# Generic error handlers (e.g. hitting a route/id type that doesn't exist)
# ---------------------------------------------------------------------
@app.errorhandler(404)
def handle_404(e):
    return error_response("The requested resource was not found.", 404)


@app.errorhandler(405)
def handle_405(e):
    return error_response("Method not allowed on this endpoint.", 405)


@app.route("/")
def index():
    return jsonify(
        {
            "message": "Task Manager API is running.",
            "endpoints": {
                "POST /tasks": "Create a new task",
                "GET /tasks": "Retrieve all tasks (optional ?status=pending|completed)",
                "GET /tasks/<id>": "Retrieve a specific task",
                "PUT /tasks/<id>": "Full update of a task",
                "PATCH /tasks/<id>": "Partial update of a task",
                "DELETE /tasks/<id>": "Delete a task",
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
