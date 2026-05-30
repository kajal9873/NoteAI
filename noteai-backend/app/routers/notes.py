from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional

from app.schemas.note import NoteCreate, NoteUpdate, NoteOut
from app.core.database import get_notes_collection
from app.core.deps import get_current_user
from app.services.ai_service import summarize_note, generate_tags

router = APIRouter(prefix="/notes", tags=["notes"])


def serialize_note(note: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    note["_id"] = str(note["_id"])
    note["user_id"] = str(note["user_id"])
    return note


def note_belongs_to_user(note: dict, user_id: str) -> bool:
    return str(note["user_id"]) == user_id


# ── GET all notes ─────────────────────────────────────
@router.get("/", response_model=list[dict])
async def get_notes(
    search: Optional[str] = Query(None),
    tag:    Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    notes_col = get_notes_collection()
    user_id   = current_user["_id"]

    query: dict = {"user_id": user_id}

    # Full-text search
    if search:
        query["$text"] = {"$search": search}

    # Tag filter
    if tag:
        query["tags"] = tag

    cursor = notes_col.find(query).sort("updated_at", -1)
    notes  = await cursor.to_list(length=100)
    return [serialize_note(n) for n in notes]


# ── GET single note ───────────────────────────────────
@router.get("/{note_id}", response_model=dict)
async def get_note(
    note_id: str,
    current_user: dict = Depends(get_current_user),
):
    notes_col = get_notes_collection()

    try:
        oid = ObjectId(note_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID")

    note = await notes_col.find_one({"_id": oid})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if not note_belongs_to_user(note, str(current_user["_id"])):
        raise HTTPException(status_code=403, detail="Access denied")

    return serialize_note(note)


# ── CREATE note ───────────────────────────────────────
@router.post("/", response_model=dict, status_code=201)
async def create_note(
    body: NoteCreate,
    current_user: dict = Depends(get_current_user),
):
    notes_col = get_notes_collection()
    now = datetime.now(timezone.utc)

    note_doc = {
        "title":      body.title,
        "content":    body.content,
        "tags":       body.tags,
        "summary":    None,
        "user_id":    current_user["_id"],
        "created_at": now,
        "updated_at": now,
    }
    result = await notes_col.insert_one(note_doc)
    note_doc["_id"] = result.inserted_id

    return serialize_note(note_doc)


# ── UPDATE note ───────────────────────────────────────
@router.put("/{note_id}", response_model=dict)
async def update_note(
    note_id: str,
    body: NoteUpdate,
    current_user: dict = Depends(get_current_user),
):
    notes_col = get_notes_collection()

    try:
        oid = ObjectId(note_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID")

    note = await notes_col.find_one({"_id": oid})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not note_belongs_to_user(note, str(current_user["_id"])):
        raise HTTPException(status_code=403, detail="Access denied")

    updates = {"updated_at": datetime.now(timezone.utc)}
    if body.title   is not None: updates["title"]   = body.title
    if body.content is not None: updates["content"] = body.content
    if body.tags    is not None: updates["tags"]    = body.tags

    await notes_col.update_one({"_id": oid}, {"$set": updates})
    updated = await notes_col.find_one({"_id": oid})
    return serialize_note(updated)


# ── DELETE note ───────────────────────────────────────
@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: str,
    current_user: dict = Depends(get_current_user),
):
    notes_col = get_notes_collection()

    try:
        oid = ObjectId(note_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID")

    note = await notes_col.find_one({"_id": oid})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not note_belongs_to_user(note, str(current_user["_id"])):
        raise HTTPException(status_code=403, detail="Access denied")

    await notes_col.delete_one({"_id": oid})


# ── AI: Summarize ─────────────────────────────────────
@router.post("/{note_id}/summarize", response_model=dict)
async def summarize(
    note_id: str,
    current_user: dict = Depends(get_current_user),
):
    notes_col = get_notes_collection()

    try:
        oid = ObjectId(note_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID")

    note = await notes_col.find_one({"_id": oid})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not note_belongs_to_user(note, str(current_user["_id"])):
        raise HTTPException(status_code=403, detail="Access denied")

    if not note.get("content", "").strip():
        raise HTTPException(status_code=400, detail="Note has no content to summarize")

    summary = await summarize_note(note["title"], note["content"])

    await notes_col.update_one(
        {"_id": oid},
        {"$set": {"summary": summary, "updated_at": datetime.now(timezone.utc)}}
    )
    updated = await notes_col.find_one({"_id": oid})
    return serialize_note(updated)


# ── AI: Auto Tag ──────────────────────────────────────
@router.post("/{note_id}/auto-tag", response_model=dict)
async def auto_tag(
    note_id: str,
    current_user: dict = Depends(get_current_user),
):
    notes_col = get_notes_collection()

    try:
        oid = ObjectId(note_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID")

    note = await notes_col.find_one({"_id": oid})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not note_belongs_to_user(note, str(current_user["_id"])):
        raise HTTPException(status_code=403, detail="Access denied")

    if not note.get("content", "").strip():
        raise HTTPException(status_code=400, detail="Note has no content to tag")

    tags = await generate_tags(note["title"], note["content"])

    await notes_col.update_one(
        {"_id": oid},
        {"$set": {"tags": tags, "updated_at": datetime.now(timezone.utc)}}
    )
    updated = await notes_col.find_one({"_id": oid})
    return serialize_note(updated)
