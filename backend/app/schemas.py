import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.models import DocumentStatus, UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    role: UserRole = UserRole.employee


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentOut(BaseModel):
    id: uuid.UUID
    title: str
    source_filename: str
    language: str
    status: DocumentStatus
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)


class SourceRef(BaseModel):
    document_id: uuid.UUID
    document_title: str
    section_label: str
    chunk_id: uuid.UUID
    excerpt: str


class SearchResponse(BaseModel):
    answer: str
    grounded: bool
    detected_language: str
    sources: list[SourceRef]
