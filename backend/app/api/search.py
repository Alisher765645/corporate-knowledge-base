from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.db import get_db
from app.models.models import SearchLog, User
from app.schemas import SearchRequest, SearchResponse, SourceRef
from app.services.llm import detect_language, generate_answer
from app.services.search import hybrid_search

router = APIRouter(prefix="/api/search", tags=["search"])
settings = get_settings()


@router.post("", response_model=SearchResponse)
def search(payload: SearchRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Пустой запрос")
    if len(query) > settings.max_query_chars:
        raise HTTPException(status_code=400, detail=f"Запрос превышает лимит в {settings.max_query_chars} символов")

    language = detect_language(query)
    results = hybrid_search(db, query)

    answer = generate_answer(query, language, results)

    db.add(
        SearchLog(
            user_id=user.id,
            query=query,
            detected_language=language,
            had_results=bool(results),
        )
    )
    db.commit()

    return SearchResponse(
        answer=answer,
        grounded=bool(results),
        detected_language=language,
        sources=[
            SourceRef(
                document_id=r["document_id"],
                document_title=r["document_title"],
                section_label=r["section_label"] or "",
                chunk_id=r["id"],
                excerpt=r["content"][:400],
            )
            for r in results
        ],
    )
