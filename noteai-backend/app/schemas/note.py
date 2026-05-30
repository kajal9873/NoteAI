from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NoteCreate(BaseModel):
    title: str = Field(default="Untitled", max_length=200)
    content: str = Field(default="")
    tags: List[str] = Field(default=[])


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteOut(BaseModel):
    id: str = Field(alias="_id")
    title: str
    content: str
    tags: List[str] = []
    summary: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
