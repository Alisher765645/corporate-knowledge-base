import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.llm import embed_text

settings = get_settings()

# Reciprocal Rank Fusion — комбинирует ранги векторного и полнотекстового поиска
RRF_K = 60


def hybrid_search(db: Session, query: str, top_k: int | None = None) -> list[dict]:
    top_k = top_k or settings.search_top_k
    query_embedding = embed_text(query)

    vector_rows = db.execute(
        text(
            """
            SELECT c.id, c.document_id, c.section_label, c.content, d.title AS document_title
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.status = 'active' AND c.embedding IS NOT NULL
            ORDER BY c.embedding <=> (:embedding)::vector
            LIMIT :limit
            """
        ),
        {"embedding": str(query_embedding), "limit": top_k * 3},
    ).mappings().all()

    fts_rows = db.execute(
        text(
            """
            SELECT c.id, c.document_id, c.section_label, c.content, d.title AS document_title
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.status = 'active'
              AND c.content_tsv @@ websearch_to_tsquery('russian', :query)
            ORDER BY ts_rank(c.content_tsv, websearch_to_tsquery('russian', :query)) DESC
            LIMIT :limit
            """
        ),
        {"query": query, "limit": top_k * 3},
    ).mappings().all()

    scores: dict[uuid.UUID, float] = {}
    rows_by_id: dict[uuid.UUID, dict] = {}

    for rank, row in enumerate(vector_rows):
        scores[row["id"]] = scores.get(row["id"], 0) + 1 / (RRF_K + rank + 1)
        rows_by_id[row["id"]] = row

    for rank, row in enumerate(fts_rows):
        scores[row["id"]] = scores.get(row["id"], 0) + 1 / (RRF_K + rank + 1)
        rows_by_id.setdefault(row["id"], row)

    ranked_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)[:top_k]

    return [dict(rows_by_id[cid]) for cid in ranked_ids]
