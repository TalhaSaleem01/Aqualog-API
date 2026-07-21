from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..auth import get_current_user
from ..database import entries_db, get_next_entry_id, seed_entries, TASK_TYPES
from ..models import EntryCreate, EntryOut, EntryUpdate
from app import limiter

router = APIRouter(prefix="/entries", tags=["Aquarium Log Entries"])

VALID_SORT_FIELDS = {"id", "tank_name", "task_type", "performed_at", "completed"}


def _find_entry(entry_id: int) -> Optional[dict]:
    return next((e for e in entries_db if e["id"] == entry_id), None)


# ---------------------------------------------------------------------
# Read — list (with filtering + sorting) and single
# ---------------------------------------------------------------------
@router.get("", response_model=List[EntryOut])
@limiter.limit("30/minute")
def list_entries(
    request: Request,
    tank_name: Optional[str] = None,
    task_type: Optional[str] = None,
    completed: Optional[bool] = None,
    sort_by: str = "id",
    order: str = "asc",
    current_user: str = Depends(get_current_user),
):
    """
    List all log entries. Supports optional filtering and sorting
    (bonus feature — not part of the base assignment):

    - ?tank_name=Reef Tank A
    - ?task_type=feeding
    - ?completed=true
    - ?sort_by=performed_at&order=desc
    """
    results = entries_db

    if tank_name:
        results = [e for e in results if e["tank_name"].lower() == tank_name.lower()]
    if task_type:
        if task_type not in TASK_TYPES:
            raise HTTPException(status_code=400, detail=f"task_type must be one of {sorted(TASK_TYPES)}")
        results = [e for e in results if e["task_type"] == task_type]
    if completed is not None:
        results = [e for e in results if e["completed"] == completed]

    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {sorted(VALID_SORT_FIELDS)}")
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    results = sorted(results, key=lambda e: e[sort_by], reverse=(order == "desc"))
    return results


# ---------------------------------------------------------------------
# Seed / reset — handy for demos and re-testing. Registered before
# "/{entry_id}" so the fixed path "/entries/reset" is matched first.
# ---------------------------------------------------------------------
@router.post("/reset", response_model=List[EntryOut])
@limiter.limit("5/minute")
def reset_entries(request: Request, current_user: str = Depends(get_current_user)):
    seed_entries()
    return entries_db


@router.get("/{entry_id}", response_model=EntryOut)
@limiter.limit("30/minute")
def get_entry(request: Request, entry_id: int, current_user: str = Depends(get_current_user)):
    entry = _find_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")
    return entry


# ---------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------
@router.post("", response_model=EntryOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("15/minute")
def create_entry(request: Request, entry: EntryCreate, current_user: str = Depends(get_current_user)):
    new_entry = {"id": get_next_entry_id(), **entry.model_dump()}
    entries_db.append(new_entry)
    return new_entry


# ---------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------
@router.put("/{entry_id}", response_model=EntryOut)
@limiter.limit("15/minute")
def update_entry(
    request: Request,
    entry_id: int,
    update: EntryUpdate,
    current_user: str = Depends(get_current_user),
):
    entry = _find_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")

    update_data = update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    entry.update(update_data)
    return entry


# ---------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------
@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("15/minute")
def delete_entry(request: Request, entry_id: int, current_user: str = Depends(get_current_user)):
    entry = _find_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")
    entries_db.remove(entry)
    return None