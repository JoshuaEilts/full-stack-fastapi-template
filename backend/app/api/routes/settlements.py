import uuid
from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models.settlement import (
    Settlement, SettlementLocation, SettlementRelationship,
    EchoDevotionHistory
)

router = APIRouter(prefix="/settlements", tags=["settlements"])

@router.post("/", response_model=Settlement)
def create_settlement(
    *,
    session: SessionDep,
    settlement_data: dict,
    _=Depends(get_current_active_superuser),
) -> Settlement:
    """Create a new settlement."""
    return crud.create_settlement(
        session=session,
        settlement_data=settlement_data
    )

@router.get("/{settlement_id}", response_model=Settlement)
def get_settlement(
    *,
    session: SessionDep,
    settlement_id: uuid.UUID,
) -> Settlement:
    """Get a specific settlement by ID."""
    if settlement := crud.get_settlement(session=session, settlement_id=settlement_id):
        return settlement
    raise HTTPException(status_code=404, detail="Settlement not found")

@router.get("/", response_model=Tuple[List[Settlement], int])
def get_settlements(
    *,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = None,
    settlement_type: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Tuple[List[Settlement], int]:
    """Get all settlements with optional filtering."""
    return crud.get_settlements(
        session=session,
        skip=skip,
        limit=limit,
        region=region,
        settlement_type=settlement_type,
        is_active=is_active
    )

@router.put("/{settlement_id}", response_model=Settlement)
def update_settlement(
    *,
    session: SessionDep,
    settlement_id: uuid.UUID,
    settlement_data: dict,
    _=Depends(get_current_active_superuser),
) -> Settlement:
    """Update a settlement's information."""
    if settlement := crud.update_settlement(
        session=session,
        settlement_id=settlement_id,
        settlement_data=settlement_data
    ):
        return settlement
    raise HTTPException(status_code=404, detail="Settlement not found")

@router.post("/{settlement_id}/locations/", response_model=SettlementLocation)
def create_location(
    *,
    session: SessionDep,
    settlement_id: uuid.UUID,
    location_data: dict,
    _=Depends(get_current_active_superuser),
) -> SettlementLocation:
    """Create a new location within a settlement."""
    if location := crud.create_settlement_location(
        session=session,
        settlement_id=settlement_id,
        location_data=location_data
    ):
        return location
    raise HTTPException(status_code=404, detail="Settlement not found")

@router.put("/relationships/", response_model=SettlementRelationship)
def update_relationship(
    *,
    session: SessionDep,
    settlement1_id: uuid.UUID,
    settlement2_id: uuid.UUID,
    relationship_score: int,
    _=Depends(get_current_active_superuser),
) -> SettlementRelationship:
    """Update or create a relationship between two settlements."""
    return crud.update_settlement_relationship(
        session=session,
        settlement1_id=settlement1_id,
        settlement2_id=settlement2_id,
        relationship_score=relationship_score
    )

@router.put("/{settlement_id}/echo-devotion", response_model=Settlement)
def update_echo_devotion(
    *,
    session: SessionDep,
    settlement_id: uuid.UUID,
    new_devotion: int,
    reason: str,
    details: Optional[dict] = None,
    _=Depends(get_current_active_superuser),
) -> Settlement:
    """Update a settlement's Echo devotion level."""
    if settlement := crud.update_settlement_echo_devotion(
        session=session,
        settlement_id=settlement_id,
        new_devotion=new_devotion,
        reason=reason,
        details=details
    ):
        return settlement
    raise HTTPException(status_code=404, detail="Settlement not found")

@router.get("/{settlement_id}/relationships/", response_model=List[SettlementRelationship])
def get_relationships(
    *,
    session: SessionDep,
    settlement_id: uuid.UUID,
) -> List[SettlementRelationship]:
    """Get all relationships for a specific settlement."""
    return crud.get_settlement_relationships(
        session=session,
        settlement_id=settlement_id
    )

@router.get("/{settlement_id}/locations/", response_model=List[SettlementLocation])
def get_locations(
    *,
    session: SessionDep,
    settlement_id: uuid.UUID,
    location_type: Optional[str] = None,
    is_public: Optional[bool] = None,
) -> List[SettlementLocation]:
    """Get all locations in a specific settlement."""
    return crud.get_settlement_locations(
        session=session,
        settlement_id=settlement_id,
        location_type=location_type,
        is_public=is_public
    )

@router.get("/{settlement_id}/echo-history/", response_model=List[EchoDevotionHistory])
def get_echo_history(
    *,
    session: SessionDep,
    settlement_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[EchoDevotionHistory]:
    """Get Echo devotion history for a specific settlement."""
    return crud.get_settlement_echo_devotion_history(
        session=session,
        settlement_id=settlement_id,
        skip=skip,
        limit=limit
    ) 