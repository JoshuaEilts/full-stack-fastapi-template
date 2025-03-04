import uuid
from datetime import datetime, time
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON, Index, ARRAY, String
from pydantic import conint

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"

class Sexuality(str, Enum):
    HETEROSEXUAL = "heterosexual"
    HOMOSEXUAL = "homosexual"
    BISEXUAL = "bisexual"
    ASEXUAL = "asexual"

class RelationType(str, Enum):
    FAMILY = "family"
    FRIEND = "friend"
    ROMANTIC = "romantic"
    PROFESSIONAL = "professional"
    ENEMY = "enemy"

class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class ActivityType(str, Enum):
    WORK = "work"
    SLEEP = "sleep"
    EAT = "eat"
    LEISURE = "leisure"
    SOCIAL = "social"
    SHOPPING = "shopping"
    WORSHIP = "worship"
    REST = "rest"

class NPCPersonality(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    npc_id: uuid.UUID = Field(foreign_key="npc.id")
    extraversion: conint(ge=0, le=100) = Field(default=50)
    agreeableness: conint(ge=0, le=100) = Field(default=50)
    conscientiousness: conint(ge=0, le=100) = Field(default=50)
    neuroticism: conint(ge=0, le=100) = Field(default=50)
    openness: conint(ge=0, le=100) = Field(default=50)
    memory_reliability: conint(ge=0, le=100) = Field(default=80)  # How well they remember details
    
    # Relationship
    npc: "NPC" = Relationship(back_populates="personality")

class NPCRelationship(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    npc1_id: uuid.UUID = Field(foreign_key="npc.id")
    npc2_id: uuid.UUID = Field(foreign_key="npc.id")
    relationship_type: RelationType
    strength: int = Field(default=0)  # -100 to 200 scale
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    
    # Additional metadata stored as JSON
    details: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    npc1: "NPC" = Relationship(back_populates="relationships_initiated", sa_relationship_kwargs={'foreign_keys': [npc1_id]})
    npc2: "NPC" = Relationship(back_populates="relationships_received", sa_relationship_kwargs={'foreign_keys': [npc2_id]})

class RelationshipHistory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    relationship_id: uuid.UUID = Field(foreign_key="npcrelationship.id")
    event_date: datetime = Field(default_factory=datetime.utcnow)
    event_type: str  # e.g., "started_dating", "married", "divorced", "became_enemies"
    description: str
    
    # Additional metadata stored as JSON
    details: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationship
    relationship: NPCRelationship = Relationship(back_populates="history")

class DailyRoutineActivity(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    npc_id: uuid.UUID = Field(foreign_key="npc.id")
    activity_type: ActivityType
    start_time: time
    end_time: time
    location_id: uuid.UUID = Field(foreign_key="settlement.id", nullable=True)
    description: str
    priority: int = Field(default=1)  # Higher number = higher priority
    
    # Relationships
    npc: "NPC" = Relationship(back_populates="routine_activities")

class WorldEvent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: str
    event_type: str  # e.g., "natural_disaster", "festival", "war", "election"
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime | None = None
    is_active: bool = Field(default=True)
    settlement_id: uuid.UUID | None = Field(foreign_key="settlement.id", nullable=True)
    
    # Impact tracking
    affected_npcs: List[uuid.UUID] = Field(default=[], sa_type=ARRAY(String))
    severity: int = Field(default=1)  # 1-10 scale
    
    # Additional data stored as JSON
    event_data: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    settlement: "Settlement" = Relationship()

class NPCEchoDevotionHistory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    npc_id: uuid.UUID = Field(foreign_key="npc.id")
    previous_devotion: int
    new_devotion: int
    change_date: datetime = Field(default_factory=datetime.utcnow)
    reason: str
    
    # Additional details about the change
    details: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationship
    npc: "NPC" = Relationship(back_populates="echo_devotion_history")

class NPC(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    age: int
    birth_date: datetime
    gender: Gender
    sexuality: Sexuality = Field(default=Sexuality.HETEROSEXUAL)
    occupation: str
    marital_status: MaritalStatus = Field(default=MaritalStatus.SINGLE)
    is_alive: bool = Field(default=True)
    location_id: uuid.UUID = Field(foreign_key="settlement.id")
    
    # Echo-related attributes
    echo_devotion: conint(ge=-100, le=100) = Field(default=50)  # Negative means rebellion
    independent_thinking: conint(ge=0, le=100) = Field(default=30)  # Higher means more likely to change Echo devotion
    
    # Stats and attributes that affect gameplay
    health: conint(ge=0, le=100) = Field(default=100)
    happiness: conint(ge=0, le=100) = Field(default=50)
    wealth: conint(ge=0, le=100) = Field(default=50)
    
    # Memory and conversation tracking
    faiss_memory_id: str = Field(nullable=True)
    last_conversation_time: datetime | None = None
    
    # Additional flexible attributes stored as JSON
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    death_date: datetime | None = None
    
    # Relationships
    personality: NPCPersonality = Relationship(back_populates="npc")
    relationships_initiated: List[NPCRelationship] = Relationship(back_populates="npc1")
    relationships_received: List[NPCRelationship] = Relationship(back_populates="npc2")
    routine_activities: List[DailyRoutineActivity] = Relationship(back_populates="npc")
    settlement: "Settlement" = Relationship(back_populates="residents")
    echo_devotion_history: List[NPCEchoDevotionHistory] = Relationship(back_populates="npc")

# Player-NPC specific relationship tracking
class PlayerNPCRelationship(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    player_id: uuid.UUID = Field(foreign_key="user.id")
    npc_id: uuid.UUID = Field(foreign_key="npc.id")
    reputation: int = Field(default=50)  # 0-100 scale
    interaction_count: int = Field(default=0)
    last_interaction: datetime | None = None
    
    # Additional metadata stored as JSON
    relationship_data: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    player: "User" = Relationship()
    npc: NPC = Relationship()

# Indexes
Index("idx_npc_name", NPC.name)
Index("idx_npc_location", NPC.location_id)
Index("idx_npc_alive", NPC.is_alive)
Index("idx_relationship_npc_pair", NPCRelationship.npc1_id, NPCRelationship.npc2_id)
Index("idx_player_npc_relationship", PlayerNPCRelationship.player_id, PlayerNPCRelationship.npc_id)

# World Event indexes
Index("idx_world_event_active_date", WorldEvent.is_active, WorldEvent.start_date)
Index("idx_world_event_settlement", WorldEvent.settlement_id)

# Daily Routine indexes
Index("idx_routine_time", DailyRoutineActivity.start_time, DailyRoutineActivity.end_time)
Index("idx_routine_activity_type", DailyRoutineActivity.activity_type)

# Relationship History indexes
Index("idx_relationship_history_date", RelationshipHistory.event_date)

# Add new index for Echo devotion history
Index("idx_npc_echo_devotion_history", 
      NPCEchoDevotionHistory.npc_id, 
      NPCEchoDevotionHistory.change_date) 