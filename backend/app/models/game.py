import uuid
from datetime import datetime
from enum import Enum
from typing import List

from sqlmodel import Field, SQLModel, Relationship

from .state import GameState

class GameDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class GameSession(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    difficulty: GameDifficulty
    status: GameStatus = Field(default=GameStatus.IN_PROGRESS)
    current_level: int = Field(default=1)
    score: int = Field(default=0)
    
    # Relationships
    user: "User" = Relationship(back_populates="game_sessions")
    game_states: List[GameState] = Relationship(back_populates="game_session") 