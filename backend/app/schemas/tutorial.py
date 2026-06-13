from typing import Literal

from pydantic import BaseModel


class LearningProgressUpdate(BaseModel):
    user_id: str = "demo_user"
    status: Literal["not_started", "in_progress", "completed", "favorited"]
    practice_notes: str = ""
