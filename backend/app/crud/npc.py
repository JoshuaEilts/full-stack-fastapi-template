import uuid
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from app.models.npc import (
    NPC, NPCPersonality, NPCRelationship, NPCEchoDevotionHistory,
    DailyRoutineActivity, RelationshipHistory
)

def create_npc(
    *,
    session: Session,
    npc_data: dict,
    personality_data: Optional[dict] = None
) -> NPC:
    # Create NPC
    db_npc = NPC(**npc_data)
    session.add(db_npc)
    session.flush()  # Flush to get the ID

    # Create personality if provided
    if personality_data:
        db_personality = NPCPersonality(npc_id=db_npc.id, **personality_data)
        session.add(db_personality)

    session.commit()
    session.refresh(db_npc)
    return db_npc

def get_npc(*, session: Session, npc_id: uuid.UUID) -> Optional[NPC]:
    return session.get(NPC, npc_id)

def get_npcs(
    session: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    settlement_id: Optional[uuid.UUID] = None,
    is_alive: Optional[bool] = None
) -> List[NPC]:
    query = select(NPC)
    
    if settlement_id:
        query = query.where(NPC.location_id == settlement_id)
    if is_alive is not None:
        query = query.where(NPC.is_alive == is_alive)
    
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()

def update_npc(
    *,
    session: Session,
    npc_id: uuid.UUID,
    npc_data: dict
) -> Optional[NPC]:
    db_npc = get_npc(session=session, npc_id=npc_id)
    if not db_npc:
        return None
    
    for key, value in npc_data.items():
        setattr(db_npc, key, value)
    
    session.add(db_npc)
    session.commit()
    session.refresh(db_npc)
    return db_npc

def create_npc_relationship(
    *,
    session: Session,
    npc1_id: uuid.UUID,
    npc2_id: uuid.UUID,
    relationship_data: dict
) -> Optional[NPCRelationship]:
    # Verify both NPCs exist
    npc1 = get_npc(session=session, npc_id=npc1_id)
    npc2 = get_npc(session=session, npc_id=npc2_id)
    if not npc1 or not npc2:
        return None

    db_relationship = NPCRelationship(
        npc1_id=npc1_id,
        npc2_id=npc2_id,
        **relationship_data
    )
    session.add(db_relationship)
    session.commit()
    session.refresh(db_relationship)
    return db_relationship

def update_echo_devotion(
    *,
    session: Session,
    npc_id: uuid.UUID,
    new_devotion: int,
    reason: str,
    details: Optional[dict] = None
) -> Optional[NPC]:
    db_npc = get_npc(session=session, npc_id=npc_id)
    if not db_npc:
        return None

    # Create history entry
    history_entry = NPCEchoDevotionHistory(
        npc_id=npc_id,
        previous_devotion=db_npc.echo_devotion,
        new_devotion=new_devotion,
        reason=reason,
        details=details or {}
    )
    session.add(history_entry)

    # Update NPC
    db_npc.echo_devotion = new_devotion
    db_npc.updated_at = datetime.utcnow()
    
    session.commit()
    session.refresh(db_npc)
    return db_npc

def add_daily_routine(
    *,
    session: Session,
    npc_id: uuid.UUID,
    routine_data: dict
) -> Optional[DailyRoutineActivity]:
    db_npc = get_npc(session=session, npc_id=npc_id)
    if not db_npc:
        return None

    db_routine = DailyRoutineActivity(npc_id=npc_id, **routine_data)
    session.add(db_routine)
    session.commit()
    session.refresh(db_routine)
    return db_routine

def get_npc_relationships(
    *,
    session: Session,
    npc_id: uuid.UUID,
    active_only: bool = True
) -> List[NPCRelationship]:
    query = select(NPCRelationship).where(
        (NPCRelationship.npc1_id == npc_id) | 
        (NPCRelationship.npc2_id == npc_id)
    )
    
    if active_only:
        query = query.where(NPCRelationship.is_active == True)
    
    return session.exec(query).all()

def get_npc_routine(
    *,
    session: Session,
    npc_id: uuid.UUID
) -> List[DailyRoutineActivity]:
    query = select(DailyRoutineActivity).where(
        DailyRoutineActivity.npc_id == npc_id
    ).order_by(DailyRoutineActivity.start_time)
    
    return session.exec(query).all()

def get_echo_devotion_history(
    *,
    session: Session,
    npc_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50
) -> List[NPCEchoDevotionHistory]:
    query = select(NPCEchoDevotionHistory).where(
        NPCEchoDevotionHistory.npc_id == npc_id
    ).order_by(NPCEchoDevotionHistory.change_date.desc())
    
    query = query.offset(skip).limit(limit)
    return session.exec(query).all() 