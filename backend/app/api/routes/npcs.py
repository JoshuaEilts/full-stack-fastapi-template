import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models.npc import (
    NPC, NPCPersonality, NPCRelationship, NPCEchoDevotionHistory,
    DailyRoutineActivity, RelationshipHistory
)

router = APIRouter(prefix="/npcs", tags=["npcs"])

@router.post("/", response_model=NPC)
def create_npc(
    *,
    session: SessionDep,
    npc_data: dict,
    personality_data: Optional[dict] = None,
    _=Depends(get_current_active_superuser),  # Only admins can create NPCs
) -> NPC:
    """Create a new NPC."""
    return crud.create_npc(
        session=session,
        npc_data=npc_data,
        personality_data=personality_data
    )

@router.get("/{npc_id}", response_model=NPC)
def get_npc(
    *,
    session: SessionDep,
    npc_id: uuid.UUID,
) -> NPC:
    """Get a specific NPC by ID."""
    if npc := crud.get_npc(session=session, npc_id=npc_id):
        return npc
    raise HTTPException(status_code=404, detail="NPC not found")

@router.get("/", response_model=List[NPC])
def get_npcs(
    *,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    settlement_id: Optional[uuid.UUID] = None,
    is_alive: Optional[bool] = None,
) -> List[NPC]:
    """Get all NPCs with optional filtering."""
    return crud.get_npcs(
        session=session,
        skip=skip,
        limit=limit,
        settlement_id=settlement_id,
        is_alive=is_alive
    )

@router.put("/{npc_id}", response_model=NPC)
def update_npc(
    *,
    session: SessionDep,
    npc_id: uuid.UUID,
    npc_data: dict,
    _=Depends(get_current_active_superuser),  # Only admins can update NPCs
) -> NPC:
    """Update an NPC's information."""
    if npc := crud.update_npc(session=session, npc_id=npc_id, npc_data=npc_data):
        return npc
    raise HTTPException(status_code=404, detail="NPC not found")

@router.post("/relationships/", response_model=NPCRelationship)
def create_relationship(
    *,
    session: SessionDep,
    npc1_id: uuid.UUID,
    npc2_id: uuid.UUID,
    relationship_data: dict,
    _=Depends(get_current_active_superuser),
) -> NPCRelationship:
    """Create a relationship between two NPCs."""
    if relationship := crud.create_npc_relationship(
        session=session,
        npc1_id=npc1_id,
        npc2_id=npc2_id,
        relationship_data=relationship_data
    ):
        return relationship
    raise HTTPException(status_code=404, detail="One or both NPCs not found")

@router.put("/{npc_id}/echo-devotion", response_model=NPC)
def update_echo_devotion(
    *,
    session: SessionDep,
    npc_id: uuid.UUID,
    new_devotion: int,
    reason: str,
    details: Optional[dict] = None,
    _=Depends(get_current_active_superuser),
) -> NPC:
    """Update an NPC's Echo devotion level."""
    if npc := crud.update_npc_echo_devotion(
        session=session,
        npc_id=npc_id,
        new_devotion=new_devotion,
        reason=reason,
        details=details
    ):
        return npc
    raise HTTPException(status_code=404, detail="NPC not found")

@router.post("/{npc_id}/routines/", response_model=DailyRoutineActivity)
def add_routine(
    *,
    session: SessionDep,
    npc_id: uuid.UUID,
    routine_data: dict,
    _=Depends(get_current_active_superuser),
) -> DailyRoutineActivity:
    """Add a daily routine activity for an NPC."""
    if routine := crud.add_daily_routine(
        session=session,
        npc_id=npc_id,
        routine_data=routine_data
    ):
        return routine
    raise HTTPException(status_code=404, detail="NPC not found")

@router.get("/{npc_id}/relationships/", response_model=List[NPCRelationship])
def get_relationships(
    *,
    session: SessionDep,
    npc_id: uuid.UUID,
    active_only: bool = True,
) -> List[NPCRelationship]:
    """Get all relationships for a specific NPC."""
    return crud.get_npc_relationships(
        session=session,
        npc_id=npc_id,
        active_only=active_only
    )

@router.get("/{npc_id}/routines/", response_model=List[DailyRoutineActivity])
def get_routines(
    *,
    session: SessionDep,
    npc_id: uuid.UUID,
) -> List[DailyRoutineActivity]:
    """Get all daily routines for a specific NPC."""
    return crud.get_npc_routine(session=session, npc_id=npc_id)

@router.get("/{npc_id}/echo-history/", response_model=List[NPCEchoDevotionHistory])
def get_echo_history(
    *,
    session: SessionDep,
    npc_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[NPCEchoDevotionHistory]:
    """Get Echo devotion history for a specific NPC."""
    return crud.get_npc_echo_devotion_history(
        session=session,
        npc_id=npc_id,
        skip=skip,
        limit=limit
    ) 