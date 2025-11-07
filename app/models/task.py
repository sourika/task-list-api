from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional
from ..db import db

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .goal import Goal
class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True, default=None)
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id")) 
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")


    def to_dict(self) -> dict:
        task_as_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }
        if self.goal_id:
            task_as_dict["goal_id"] = self.goal_id
        return task_as_dict


    @classmethod
    def from_dict(cls, data: dict):
        if "title" not in data:
            raise KeyError("title")
        if "description" not in data:
            raise KeyError("description")
        task = cls(
                title=data["title"],
                description=data["description"],
                completed_at=None,
            )  
        if "goal_id" in data:
            task.goal_id = data["goal_id"]
        return task  