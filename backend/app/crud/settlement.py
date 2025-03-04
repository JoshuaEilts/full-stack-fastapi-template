import uuid
from typing import List, Optional, Tuple
from datetime import datetime
from sqlmodel import Session, select

from app.models.settlement import (
    Settlement, SettlementLocation, SettlementRelationship,
    EchoDevotionHistory
)

def create_settlement(
    *,
    session: Session,
    settlement_data: dict
) -> Settlement:
    db_settlement = Settlement(**settlement_data)
    session.add(db_settlement)
    session.commit()
    session.refresh(db_settlement)
    return db_settlement

def get_settlement(
    *,
    session: Session,
    settlement_id: uuid.UUID
) -> Optional[Settlement]:
    return session.get(Settlement, settlement_id)

def get_settlements(
    session: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = None,
    settlement_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[Settlement], int]:
    query = select(Settlement)
    
    if region:
        query = query.where(Settlement.region == region)
    if settlement_type:
        query = query.where(Settlement.settlement_type == settlement_type)
    if is_active is not None:
        query = query.where(Settlement.is_active == is_active)
    
    total = session.exec(query).all()
    settlements = session.exec(query.offset(skip).limit(limit)).all()
    return settlements, len(total)

def update_settlement(
    *,
    session: Session,
    settlement_id: uuid.UUID,
    settlement_data: dict
) -> Optional[Settlement]:
    db_settlement = get_settlement(session=session, settlement_id=settlement_id)
    if not db_settlement:
        return None
    
    for key, value in settlement_data.items():
        setattr(db_settlement, key, value)
    
    session.add(db_settlement)
    session.commit()
    session.refresh(db_settlement)
    return db_settlement

def create_settlement_location(
    *,
    session: Session,
    settlement_id: uuid.UUID,
    location_data: dict
) -> Optional[SettlementLocation]:
    db_settlement = get_settlement(session=session, settlement_id=settlement_id)
    if not db_settlement:
        return None

    db_location = SettlementLocation(settlement_id=settlement_id, **location_data)
    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    return db_location

def update_settlement_relationship(
    *,
    session: Session,
    settlement1_id: uuid.UUID,
    settlement2_id: uuid.UUID,
    relationship_score: int
) -> Optional[SettlementRelationship]:
    # Check if relationship exists
    query = select(SettlementRelationship).where(
        ((SettlementRelationship.settlement1_id == settlement1_id) &
         (SettlementRelationship.settlement2_id == settlement2_id)) |
        ((SettlementRelationship.settlement1_id == settlement2_id) &
         (SettlementRelationship.settlement2_id == settlement1_id))
    )
    db_relationship = session.exec(query).first()
    
    if db_relationship:
        db_relationship.relationship_score = relationship_score
        db_relationship.last_updated = datetime.utcnow()
    else:
        db_relationship = SettlementRelationship(
            settlement1_id=settlement1_id,
            settlement2_id=settlement2_id,
            relationship_score=relationship_score
        )
    
    session.add(db_relationship)
    session.commit()
    session.refresh(db_relationship)
    return db_relationship

def update_echo_devotion(
    *,
    session: Session,
    settlement_id: uuid.UUID,
    new_devotion: int,
    reason: str,
    details: Optional[dict] = None
) -> Optional[Settlement]:
    db_settlement = get_settlement(session=session, settlement_id=settlement_id)
    if not db_settlement:
        return None

    # Create history entry
    history_entry = EchoDevotionHistory(
        settlement_id=settlement_id,
        previous_devotion=db_settlement.echo_devotion,
        new_devotion=new_devotion,
        reason=reason,
        details=details or {}
    )
    session.add(history_entry)

    # Update Settlement
    db_settlement.echo_devotion = new_devotion
    db_settlement.updated_at = datetime.utcnow()
    
    session.commit()
    session.refresh(db_settlement)
    return db_settlement

def get_settlement_relationships(
    *,
    session: Session,
    settlement_id: uuid.UUID
) -> List[SettlementRelationship]:
    query = select(SettlementRelationship).where(
        (SettlementRelationship.settlement1_id == settlement_id) |
        (SettlementRelationship.settlement2_id == settlement_id)
    )
    return session.exec(query).all()

def get_settlement_locations(
    *,
    session: Session,
    settlement_id: uuid.UUID,
    location_type: Optional[str] = None,
    is_public: Optional[bool] = None
) -> List[SettlementLocation]:
    query = select(SettlementLocation).where(
        SettlementLocation.settlement_id == settlement_id
    )
    
    if location_type:
        query = query.where(SettlementLocation.location_type == location_type)
    if is_public is not None:
        query = query.where(SettlementLocation.is_public == is_public)
    
    return session.exec(query).all()

def get_echo_devotion_history(
    *,
    session: Session,
    settlement_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50
) -> List[EchoDevotionHistory]:
    query = select(EchoDevotionHistory).where(
        EchoDevotionHistory.settlement_id == settlement_id
    ).order_by(EchoDevotionHistory.change_date.desc())
    
    query = query.offset(skip).limit(limit)
    return session.exec(query).all() 