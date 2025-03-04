import uuid
from datetime import datetime
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel, Relationship

class GameState(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    game_session_id: uuid.UUID = Field(foreign_key="gamesession.id")
    saved_at: datetime = Field(default_factory=datetime.utcnow)
    state_data: dict = Field(default={}, sa_type=JSON)
    checkpoint_name: str | None = None
    
    # Relationships
    game_session: "GameSession" = Relationship(back_populates="game_states") 