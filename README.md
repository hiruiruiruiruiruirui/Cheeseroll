# AI Student Study Assistant (AI学习资料整理助手)

Upload PPT, Word, or PDF study materials — get AI-organized review notes and A4 PDF export.

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Anthropic Claude API key
- Tencent Cloud COS bucket (for file storage)
- WeChat Mini Program AppID (for login)

### Setup

```bash
# Clone the repo
git clone <repo-url> && cd student-study-assistant

# Copy and configure environment
cp .env.example .env
# Edit .env with your actual keys

# Start services (PostgreSQL, Redis, API, Celery worker)
cd backend
docker-compose up -d

# The API is now running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Manual (without Docker)

```bash
# Start PostgreSQL and Redis manually, then:

cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

# Initialize database
psql -U postgres -c "CREATE DATABASE study_assistant;"
psql -U postgres -d study_assistant -f ../scripts/init_db.sql

# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info &

# Start API server
uvicorn app.main:app --reload
```

## Project Structure

```
student-study-assistant/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── models/    # SQLAlchemy ORM models
│   │   ├── schemas/   # Pydantic request/response schemas
│   │   ├── services/  # Business logic (doc parse, AI, PDF, files)
│   │   ├── middleware/ # Auth, subscription, rate limiting
│   │   ├── tasks/     # Celery async tasks
│   │   └── utils/     # Prompts, COS client, WeChat helpers
│   └── tests/
├── miniprogram/       # Native WeChat Mini Program
├── web/               # Vue3 Web frontend (Vite SPA)
├── scripts/           # SQL DDL and seed data
└── docs/              # Documentation
```

## API Endpoints

All under `/api/v1`:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/wechat-login` | No | Login with WeChat code |
| GET | `/auth/me` | Yes | Get current user |
| POST | `/upload` | Yes | Upload a file |
| POST | `/process` | Yes | Start AI processing |
| GET | `/process/{id}/status` | Yes | Poll processing status |
| GET | `/records` | Yes | List user's records |
| GET | `/records/{id}` | Yes | Get record with Markdown |
| GET | `/records/{id}/pdf` | Yes | Download PDF |

## Environment Variables

See `.env.example` for the full list. Required:

- `SECRET_KEY` — JWT signing key
- `DATABASE_URL` — PostgreSQL connection string
- `ANTHROPIC_API_KEY` — Claude API key
- `WECHAT_APPID` + `WECHAT_SECRET` — Mini Program credentials
- `COS_SECRET_ID` + `COS_SECRET_KEY` — Tencent COS access

## License

Proprietary. All rights reserved.
