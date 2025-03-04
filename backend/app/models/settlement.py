import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON, Index, ARRAY, String
from pydantic import conint

class SettlementType(str, Enum):
    CITY = "city"
    VILLAGE = "village"

class SettlementRelationType(str, Enum):
    ALLIED = "allied"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    TRADE_PARTNERS = "trade_partners"
    VASSAL = "vassal"
    OVERLORD = "overlord"

class EconomyType(str, Enum):
    CROPS = "crops"
    LIVESTOCK = "livestock"
    ORE = "ore"
    WINE = "wine"
    HERBS = "herbs"

class EchoDevotionHistory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    settlement_id: uuid.UUID = Field(foreign_key="settlement.id")
    previous_devotion: int
    new_devotion: int
    change_date: datetime = Field(default_factory=datetime.utcnow)
    reason: str
    
    # Additional details about the change
    details: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationship
    settlement: "Settlement" = Relationship(back_populates="devotion_history")

class Settlement(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    settlement_type: SettlementType
    population: int = Field(default=0)
    founded_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Location
    coordinates_x: float  # Game world coordinates
    coordinates_y: float
    region: str = Field(index=True)
    
    # Economic factors
    primary_economy: EconomyType
    secondary_economy: EconomyType | None = None
    wealth_rating: conint(ge=0, le=100) = Field(default=50)
    trade_activity: conint(ge=0, le=100) = Field(default=50)
    
    # Echo-related attributes
    echo_devotion: conint(ge=-100, le=100) = Field(default=50)  # Negative means rebellion
    independent_thinking: conint(ge=0, le=100) = Field(default=30)  # Higher means more likely to change Echo devotion
    
    # Status indicators
    is_active: bool = Field(default=True)
    safety_rating: conint(ge=0, le=100) = Field(default=50)
    quality_of_life: conint(ge=0, le=100) = Field(default=50)
    
    # Cultural and social aspects
    cultural_traits: List[str] = Field(default=[], sa_type=ARRAY(String))
    notable_features: List[str] = Field(default=[], sa_type=ARRAY(String))
    
    # Additional data stored as JSON
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    residents: List["NPC"] = Relationship(back_populates="settlement")
    events: List["WorldEvent"] = Relationship(back_populates="settlement")
    locations: List["SettlementLocation"] = Relationship(back_populates="settlement")
    devotion_history: List[EchoDevotionHistory] = Relationship(back_populates="settlement")

class SettlementLocation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    settlement_id: uuid.UUID = Field(foreign_key="settlement.id")
    name: str
    location_type: str  # e.g., "tavern", "market", "temple", "house"
    description: str
    capacity: int | None = None
    is_public: bool = Field(default=True)
    
    # Location within settlement
    coordinates_x: float | None = None
    coordinates_y: float | None = None
    
    # Additional data stored as JSON
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    settlement: Settlement = Relationship(back_populates="locations")

class SettlementRelationship(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    settlement1_id: uuid.UUID = Field(foreign_key="settlement.id")
    settlement2_id: uuid.UUID = Field(foreign_key="settlement.id")
    relationship_score: conint(ge=0, le=100) = Field(default=50)  # 0=enemies, 100=friends
    start_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Trade details
    trade_volume: int = Field(default=0)
    
    # Additional data stored as JSON
    details: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    settlement1: Settlement = Relationship(sa_relationship_kwargs={'foreign_keys': [settlement1_id]})
    settlement2: Settlement = Relationship(sa_relationship_kwargs={'foreign_keys': [settlement2_id]})

# Indexes
Index("idx_settlement_name", Settlement.name)
Index("idx_settlement_region", Settlement.region)
Index("idx_settlement_type", Settlement.settlement_type)
Index("idx_settlement_population", Settlement.population)
Index("idx_settlement_coordinates", Settlement.coordinates_x, Settlement.coordinates_y)

Index("idx_settlement_location_type", SettlementLocation.location_type)
Index("idx_settlement_location_public", SettlementLocation.is_public)

Index("idx_settlement_relationship_pair", 
      SettlementRelationship.settlement1_id, 
      SettlementRelationship.settlement2_id)

Index("idx_echo_devotion_history", 
      EchoDevotionHistory.settlement_id, 
      EchoDevotionHistory.change_date) 