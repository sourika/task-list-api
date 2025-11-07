from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from ..db import db

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .task import Task

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
        }


    @classmethod
    def from_dict(cls, data: dict):
        if "title" not in data:
            raise KeyError("title")
        return cls(
                title=data["title"]
            )