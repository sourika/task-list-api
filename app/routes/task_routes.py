from flask import Blueprint, Response, abort, make_response, request
from app.models.task import Task
from ..db import db
from sqlalchemy import asc, desc

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# helpers
def get_task_by_id(task_id):
    try:
        task_id = int(task_id)
    except (TypeError, ValueError):
        return abort(make_response({"message": f"Task id {task_id} invalid"}, 400))
    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)
    if not task:
        return abort(make_response({"message": f"Task id {task_id} not found"}, 404))

    return task


def create_instance_from_dict(data: dict, factory):
    try:
        instance = factory(data)              
    except (KeyError, ValueError):
        return abort(make_response({"details": "Invalid data"}, 400))
    db.session.add(instance)
    db.session.commit()
    return instance, 201    


def parse_json_object():
    """Return dict or 400 {'details': 'Invalid data'}."""
    data = request.get_json(silent=True) # don’t raise BadRequest on invalid JSON — just return None.
    if not isinstance(data, dict):
        abort(make_response({"details": "Invalid data"}, 400))
    return data


# routes
@tasks_bp.post("")
def create_task():
    data = parse_json_object() 
    task, status = create_instance_from_dict(data, Task.from_dict)
    return task.to_dict(), status


@tasks_bp.get("")
def get_all_tasks():
    sort = request.args.get("sort")
    if sort == "asc":
        query = db.select(Task).order_by(Task.title.asc())
    elif sort == "desc":
        query = db.select(Task).order_by(Task.title.desc())
    else:    
        query = db.select(Task).order_by(Task.id)
    tasks = db.session.scalars(query).all()
    return [t.to_dict() for t in tasks], 200


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = get_task_by_id(task_id)
    return task.to_dict(), 200


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = get_task_by_id(task_id)
    data = parse_json_object()
    try:
        task.title = data["title"]
        task.description = data["description"]
    except KeyError:
        return abort(make_response({"details": "Invalid data"}, 400))
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = get_task_by_id(task_id)
    db.session.delete(task)
    db.session.commit()
    return Response(status=204, mimetype="application/json")