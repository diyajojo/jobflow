# Job Autofiller — Backend

Autonomous agentic job application system. Parses resumes, scrapes LinkedIn jobs, scores fit with AI, and generates tailored answers for application forms — powering a Chrome Extension.

## Stack

- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL via SQLModel
- **Queue:** Redis + Celery (async tasks)
- **AI:** Groq API — Llama 3.1 (scoring) / Llama 3.3 (answers)
- **PDF Parsing:** Docling
- **Job Scraping:** Apify (LinkedIn)

## Quick Start

**Prerequisites:** Docker + Docker Compose. `uv` is auto-installed by `setup.sh` if not present.

**Step 1 — Copy env and add API keys**
```bash
cp .env.example .env
```
Open `.env` and set:
```
GROQ_API_KEY=your_groq_api_key_here
APIFY_API_TOKEN=your_apify_token_here
```
> Need an Apify token? See [docs/get-apify-token.md](docs/get-apify-token.md).

**Step 2 — Run setup**
```bash
./setup.sh
```
This installs dependencies, starts the `db` and `redis` Docker containers, and runs DB migrations.

**Step 3 — Start the API server and Celery worker (two terminals)**

Terminal 1:
```bash
uv run uvicorn app.main:app --reload
```

Terminal 2:
```bash
uv run celery -A app.worker.celery_app worker --loglevel=info
```

> **macOS Users:** If you encounter `WorkerLostError` or process forking issues, use the `--pool=solo` option:
> ```bash
> uv run celery -A app.worker.celery_app worker --pool=solo --loglevel=info
> ```
> This avoids fork-safety issues on macOS (especially on Apple Silicon or newer macOS versions).

Both must be running — the Celery worker handles all async tasks (resume parsing, job scraping, scoring).

**Step 4 — Verify**
```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

Interactive docs: `http://localhost:8000/docs`

**Stopping**
```bash
# API server / Celery worker: Ctrl+C in each terminal
docker-compose down
```

## System Workflow

The typical end-to-end flow has five stages:

```
1. Upload Resume  →  async parse (Docling PDF → Markdown)
2. Discover Jobs  →  async scrape LinkedIn (Apify)
3. Score Jobs     →  async AI scoring (Groq Llama 3.1, 1–10 fit score)
4. List Jobs      →  sorted by score, filter by search session
5. Fill Forms     →  AI-generated answers per application question (REST or WebSocket)
```

A default user (`id=1`, `email=local@autofiller.dev`) is seeded at startup for local use.

> [!NOTE]
> **No authentication by design.** JobFlow is a local-first, single-user tool. All endpoints use a hardcoded `user_id=1` — there is no login, JWT, or multi-user support. This is intentional; adding auth is tracked as a future enhancement for if/when the project moves to a hosted model.

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/job_autofiller` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `GROQ_API_KEY` | — | **Required.** Groq API key |
| `APIFY_API_TOKEN` | — | **Required.** Apify token |
| `SCORING_MODEL` | `llama-3.1-8b-instant` | Model for job scoring (500K TPD) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Model for answer generation (100K TPD) |

## Project Structure

```
app/
├── api/            # FastAPI routers (thin HTTP layer only)
├── models/         # SQLModel table definitions
├── services/       # Stateless business logic
│   ├── parsing.py      # Docling: PDF bytes → Markdown
│   ├── discovery.py    # Apify: title + location → job list
│   ├── reasoning.py    # Groq: resume + JD → fit score
│   └── extension.py    # Groq: resume + JD + question → answer
└── worker/         # Celery task definitions
```

## API Reference

See [docs/api.md](docs/api.md) for full endpoint documentation.

## Running Tests

```bash
uv run pytest
```
