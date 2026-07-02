import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.db import get_db
from app.models.models import Document, DocumentChunk, DocumentStatus, User
from app.schemas import DocumentOut
from app.services.chunking import split_into_chunks
from app.services.llm import embed_texts
from app.services.text_extraction import extract_text

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")


@router.post("", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile,
    title: str | None = None,
    language: str = "ru",
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if not file.filename or not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail=f"Поддерживаемые форматы: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    raw_text = extract_text(file.filename, content)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Не удалось извлечь текст из документа")

    document = Document(
        title=title or file.filename,
        source_filename=file.filename,
        language=language,
        status=DocumentStatus.active,
        uploaded_by=admin.id,
    )
    db.add(document)
    db.flush()

    chunk_dicts = split_into_chunks(raw_text)
    if not chunk_dicts:
        raise HTTPException(status_code=400, detail="Документ пуст после обработки")

    embeddings = embed_texts([c["content"] for c in chunk_dicts])

    for index, (chunk, embedding) in enumerate(zip(chunk_dicts, embeddings)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                section_label=chunk["section_label"],
                content=chunk["content"],
                embedding=embedding,
            )
        )
    db.commit()
    db.refresh(document)

    db.execute(
        text(
            "UPDATE document_chunks SET content_tsv = to_tsvector('russian', content) "
            "WHERE document_id = :doc_id"
        ),
        {"doc_id": document.id},
    )
    db.commit()

    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.patch("/{document_id}/archive", response_model=DocumentOut)
def archive_document(document_id: uuid.UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    document.status = DocumentStatus.archived
    db.commit()
    db.refresh(document)
    return document
