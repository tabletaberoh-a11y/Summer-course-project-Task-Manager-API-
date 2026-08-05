"""
app.py — Task Manager API

A RESTful CRUD API for managing tasks, built with Flask and backed by a
real SQLite database (via Flask-SQLAlchemy).

Data model (Task):
    id           - int, auto-generated, unique (primary key)
    title        - string, required, cannot be empty
    description  - string, optional
    status       - string, "pending" or "completed" (defaults to "pending")
    created_at   - ISO 8601 timestamp, auto-generated

Storage:
    Tasks are persisted in a SQLite database file (`tasks.db`), created
    automatically the first time the app runs. Unlike in-memory storage,
    data now survives server restarts. SQLAlchemy is used as the ORM
    layer so the database can later be swapped for PostgreSQL/MySQL by
    only changing the `SQLALCHEMY_DATABASE_URI` — no route code changes
    needed.
"""

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'tasks.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

VALID_STATUSES = {"pending", "completed"}


# ---------------------------------------------------------------------
# Database model
# ---------------------------------------------------------------------
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True, default="")
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(
        db.String(64), nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "status": self.status,
            "created_at": self.created_at,
        }


def error_response(message, status_code):
    """Uniform JSON error shape for every failure case."""
    return jsonify({"error": message}), status_code


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

    task = Task(
        title=str(title).strip(),
        description=data.get("description", "") or "",
        status=status,
    )
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


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

    query = Task.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    tasks = query.order_by(Task.id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


# ---------------------------------------------------------------------
# GET /tasks/<id> — Retrieve a specific task
# ---------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return error_response(f"Task with id {task_id} not found.", 404)
    return jsonify(task.to_dict()), 200


# ---------------------------------------------------------------------
# PUT/PATCH /tasks/<id> — Update an existing task
# ---------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["PUT", "PATCH"])
def update_task(task_id):
    task = db.session.get(Task, task_id)
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
        task.title = str(data["title"]).strip()

    if "description" in data:
        task.description = data["description"] or ""

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return error_response(
                f"'status' must be one of {sorted(VALID_STATUSES)}.", 400
            )
        task.status = data["status"]

    db.session.commit()
    return jsonify(task.to_dict()), 200


# ---------------------------------------------------------------------
# DELETE /tasks/<id> — Remove a task
# ---------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return error_response(f"Task with id {task_id} not found.", 404)

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Task with id {task_id} deleted successfully."}), 200


# ---------------------------------------------------------------------
# Generic error handlers
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
            "database": "SQLite (tasks.db)",
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


# Create the database tables (and the tasks.db file) automatically the
# first time the app starts, if they don't already exist.
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
