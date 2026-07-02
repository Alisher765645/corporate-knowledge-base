# Корпоративная база знаний по нормативным документам (MVP1)

Реализация MVP1 из [PRD_1.md](./PRD_1.md): текстовый поиск и Q&A на русском языке,
загрузка документов администратором, гибридный поиск (векторный + полнотекстовый).

## Стек

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL + pgvector
- **Frontend:** React (Vite) + TypeScript
- **LLM/эмбеддинги:** OpenAI-совместимый API (настраивается через `.env`)

## Возможности MVP1

- Загрузка, обновление и архивирование документов (PDF, DOCX, TXT) — только роль `admin`
- Автоматический чанкинг документов и генерация эмбеддингов
- Гибридный поиск: полнотекстовый (Postgres `tsvector`) + векторный (`pgvector`)
- Q&A по естественному языку с ответом строго по найденным фрагментам (RAG)
- Ответ всегда содержит ссылки на источник (документ + фрагмент)
- Если релевантных фрагментов нет — система явно об этом сообщает, а не придумывает ответ
- Лимит ввода — 5000 символов со счётчиком в интерфейсе
- Простая ролевая модель (`admin` / `employee`)

## Вне рамок MVP1 (см. дорожную карту в PRD)

Казахский язык, голосовой и фото-ввод, расширенный аудит-лог — запланированы в MVP2-4.

## Запуск

### Backend

```bash
cd backend
cp .env.example .env   # заполнить OPENAI_API_KEY и DATABASE_URL
python -m venv venv && source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### База данных

Требуется PostgreSQL с расширением `pgvector`. Быстрый старт через Docker:

```bash
docker compose up -d
```

## Структура проекта

```
backend/
  app/
    api/          # роуты FastAPI (documents, search, auth)
    core/         # конфиг, безопасность, зависимости
    models/       # SQLAlchemy-модели
    services/     # чанкинг, эмбеддинги, гибридный поиск, RAG
  migrations/      # Alembic
frontend/
  src/
    components/   # SearchBox, AnswerCard, DocumentList, UploadForm
```
