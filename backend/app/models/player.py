import uuid
from datetime import datetime
from typing import List
from sqlalchemy import ARRAY, String

from sqlmodel import Field, SQLModel, Relationship

class PlayerProgress(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    highest_level_reached: int = Field(default=1)
    total_score: int = Field(default=0)
    achievements_unlocked: List[str] = Field(default=[], sa_type=ARRAY(String))
    last_played_at: datetime | None = None
    
    # Relationships
    user: "User" = Relationship(back_populates="progress") 