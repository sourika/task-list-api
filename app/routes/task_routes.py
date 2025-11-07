from flask import Blueprint, Response, abort, make_response, request
from datetime import datetime
from app.models.task import Task
from .route_utilities import validate_model, create_model
from ..db import db
from sqlalchemy import asc, desc
import os, requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def send_slack_message(text: str):
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        return
    try:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json={"channel": SLACK_CHANNEL_ID, "text": text},
            timeout=5,
        )
        
        if resp.status_code != 200 or not resp.json().get("ok", False):
            pass
    except Exception:
        pass

@bp.post("")
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)

@bp.get("")
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


@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict(), 200

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()
    try:
        task.title = request_body["title"]
        task.description = request_body["description"]
    except KeyError:
        return abort(make_response({"details": "Invalid data"}, 400))
    db.session.commit()
    return Response(status=204, mimetype="application/json")

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    return Response(status=204, mimetype="application/json")

@bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()
    db.session.commit()
    send_slack_message(f"Someone just completed the task {task.title}")
    return Response(status=204, mimetype="application/json")

@bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()
    return Response(status=204, mimetype="application/json")