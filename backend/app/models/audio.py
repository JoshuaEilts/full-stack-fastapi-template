import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

class AudioAssetType(str, Enum):
    VOICE = "voice"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    AMBIENT = "ambient"

class AudioAsset(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    type: AudioAssetType
    file_path: str
    duration_seconds: float
    level: int | None = None
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow) 