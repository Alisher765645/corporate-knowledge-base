from openai import OpenAI

from app.core.config import get_settings

settings = get_settings()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    return _client


def embed_text(text: str) -> list[float]:
    response = get_client().embeddings.create(model=settings.embedding_model, input=text)
    return response.data[0].embedding


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    response = get_client().embeddings.create(model=settings.embedding_model, input=texts)
    return [item.embedding for item in response.data]


def detect_language(text: str) -> str:
    """Грубая эвристика ru/kk по характерным казахским буквам; уточняется LLM при необходимости."""
    kazakh_letters = set("әғқңөұүһі")
    lowered = text.lower()
    if any(ch in kazakh_letters for ch in lowered):
        return "kk"
    return "ru"


def generate_answer(query: str, language: str, context_chunks: list[dict]) -> str:
    if not context_chunks:
        if language == "kk":
            return "Кешіріңіз, бұл сұрақ бойынша база құжаттарынан тиісті ақпарат табылмады."
        return "К сожалению, по этому вопросу в базе документов не найдено релевантной информации."

    context_text = "\n\n".join(
        f"[Источник {i + 1}: {c['document_title']}"
        f"{', раздел ' + c['section_label'] if c['section_label'] else ''}]\n{c['content']}"
        for i, c in enumerate(context_chunks)
    )

    system_prompt = (
        "Ты — ассистент корпоративной базы знаний по нормативным документам. "
        "Отвечай СТРОГО на основе предоставленных фрагментов документов, ничего не выдумывай. "
        "Если в фрагментах нет ответа на вопрос — прямо скажи об этом. "
        "Всегда указывай, на какой источник опирается каждое утверждение, ссылаясь на номер источника в квадратных скобках, например [Источник 1]. "
        f"Отвечай на языке: {'казахском' if language == 'kk' else 'русском'}."
    )

    response = get_client().chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Фрагменты документов:\n\n{context_text}\n\nВопрос: {query}"},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content or ""
