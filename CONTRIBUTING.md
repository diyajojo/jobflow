# Contributing to JobFlow

First off, thank you for contributing to JobFlow! 🎉  
Whether you're fixing a bug, improving docs, or building a new feature — every contribution counts.

---

## Table of Contents

- [GSSoC Participation](#-gsoc-participation)
- [Understanding the Project](#-understanding-the-project)
- [Setting Up Your Environment](#-setting-up-your-environment)
- [Finding an Issue to Work On](#-finding-an-issue-to-work-on)
- [Contribution Workflow](#-contribution-workflow)
- [Code Standards](#-code-standards)
- [Getting Help](#-getting-help)

---

## 🌸 GSSoC Participation

JobFlow participates in **GirlScript Summer of Code (GSSoC)**. Here's how to participate:

1. **Find an issue** labeled `gssoc` or `good first issue` on the [issues page](https://github.com/mehrinshamim/mini-project/issues).
2. **Comment on the issue** to express your interest — don't submit a PR without claiming an issue first.
3. **Wait for assignment** — a maintainer will assign it to you (usually within 24–48 hrs).
4. **Fork, work, and submit a PR** — link your PR to the issue using `Closes #<issue-number>`.
5. **One issue at a time** — please don't claim multiple issues simultaneously.

### PR Labels

Maintainers apply these labels during review. Every merged PR is scored using them.

#### Difficulty (required)

| Label | Description |
|-------|-------------|
| `level:beginner` | Minimal code change, no architectural knowledge needed |
| `level:intermediate` | Requires reading existing code and understanding context |
| `level:advanced` | Significant feature work, cross-component changes |
| `level:critical` | Core architecture, breaking changes, or security-sensitive |

#### Quality (optional)

| Label | Description |
|-------|-------------|
| `quality:clean` | Well-structured code, good tests, clear commit messages |
| `quality:exceptional` | Outstanding contribution — above and beyond expectations |

#### Type (optional)

| Label | Description |
|-------|-------------|
| `type:bug` | Bug fix |
| `type:feature` | New feature |
| `type:docs` | Documentation improvement |
| `type:testing` | Adding or improving tests |
| `type:security` | Security fix or hardening |
| `type:performance` | Performance optimization |
| `type:design` | UI/UX design improvement |
| `type:refactor` | Code restructure without behavior change |

### Scoring

- **`gssoc:approved`** is added to every accepted PR and awards **+50 base points**.
- Mentors add **`mentor:username`** to PRs they reviewed to earn mentor points.
- **Score formula:**

  ```
  Score = 50 + (difficulty × quality) + type_bonus
  ```

---

## 📚 Understanding the Project

Before writing code, take 10–15 minutes to understand the architecture:

1. **Read the root [`README.md`](README.md)** — overview, setup, feature list
2. **Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** — how the 3 components connect, data flow diagrams
3. **Browse [`backend/docs/log.md`](backend/docs/log.md)** — engineering journal explaining *why* key decisions were made (highly recommended!)
4. **Explore the API** — after starting the backend, visit `http://localhost:8000/docs` for interactive Swagger docs

> [!NOTE]
> **Single-user, local-first.** JobFlow runs on `localhost` with a single seeded user (`user_id=1`). There is no authentication or multi-user support — this is by design. Please don't file issues about missing auth or IDOR on endpoints; see [ARCHITECTURE.md](docs/ARCHITECTURE.md#why-user_id1-everywhere-local-first-single-user) for details.

### Quick Mental Model

```
User browser (Next.js frontend)
  ↕ REST API
FastAPI backend  ←→  Celery workers (async jobs)
  ↕ DB              ↕ Redis broker
  PostgreSQL        ↕ Groq (AI)  +  Apify (scraping)

Chrome Extension (separate, connects to backend)
  content.js (in-page form scraper/filler)
  background.js (API relay)
  popup.js (user interface)
```

---

## 🛠️ Setting Up Your Environment

### Prerequisites

- **Python 3.12+** and [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- **Node.js 18+** and `npm`
- **Docker + Docker Compose**
- **Google Chrome** (for extension development)

### Full Setup (with API keys)

For full functionality you'll need:
- **Groq API key** — free tier available at [console.groq.com](https://console.groq.com)
- **Apify token** — see [`backend/docs/get-apify-token.md`](backend/docs/get-apify-token.md)

```bash
# 1. Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/mini-project.git
cd mini-project

# 2. Backend setup
cd backend
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and APIFY_API_TOKEN

# 3. Start Docker services (PostgreSQL + Redis) and run migrations
./setup.sh

# 4. Start the API server (Terminal 1)
uv run uvicorn app.main:app --reload

# 5. Start the Celery worker (Terminal 2)
uv run celery -A app.worker.celery_app worker --loglevel=info

# 6. Frontend setup (Terminal 3)
cd ../frontend
npm install
npm run dev
# Visit http://localhost:3000

# 7. Load the Chrome Extension
# chrome://extensions/ → Enable Developer Mode → Load Unpacked → select extension/
```

### Contributing Without API Keys

Many issues — especially frontend, docs, testing, and DX tasks — **don't require Groq or Apify**. To run the frontend without a live backend:

1. Look for issues labeled `no-api-needed` or `frontend` or `docs`
2. The dashboard renders correctly without a backend for UI/styling work
3. Check the issue description — many UI issues have mock data you can use

---

## 🔍 Finding an Issue to Work On

### Good First Issues

These require minimal setup and are ideal for first-time contributors:

- Replace `alert()` calls with inline error messages
- Add file size validation to resume upload (UI shows "5MB max" but doesn't enforce it)
- Sort job results by score descending
- Deduplicate the footer component across pages
- Fix double font loading in `layout.tsx`
- Add extension `README.md`
- Fix the extension name to be consistent ("Job Autofiller" vs "JobFlow")

Browse all good-first-issues: [github.com/mehrinshamim/mini-project/labels/good%20first%20issue](https://github.com/mehrinshamim/mini-project/labels/good%20first%20issue)

### Intermediate Issues

- Extract API base URL to `NEXT_PUBLIC_API_URL` env var
- Add polling timeout + retry logic for job search
- Add `parse_status` field to Resume model
- Create GitHub Actions CI pipeline
- Add pagination + sorting to `GET /jobs/`

### Advanced Issues

- Implement LLM provider abstraction (Groq + Ollama for local AI)
- Add JWT authentication (breaking change — discuss first)
- Add embedding-based job pre-filter (saves Groq API quota)
- Add SSE streaming for real-time scoring progress

---

## 🔄 Contribution Workflow

```
1. Comment on an issue to claim it
2. Fork the repo on GitHub
3. Clone your fork locally
4. Create a branch:
     git checkout -b feature/descriptive-name
     # or: git checkout -b fix/issue-123-short-description
5. Make your changes
6. Test your changes manually
7. Commit with a descriptive message:
     git commit -m "fix: replace alert() with inline error state in ResumeSection"
8. Push and open a Pull Request
9. Link the PR to the issue: "Closes #123"
10. Wait for review — respond to feedback within 48 hours
```

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/short-name` | `feature/sort-jobs-by-score` |
| Bug fix | `fix/issue-N-description` | `fix/123-cors-credentials` |
| Docs | `docs/what-you-added` | `docs/extension-readme` |
| Testing | `test/what-youre-testing` | `test/resume-upload-api` |

---

## 📐 Code Standards

### Python (Backend)

- **Formatter:** `ruff format` (configured in `pyproject.toml`)
- **Linter:** `ruff check` 
- **Type hints:** Required for all new functions
- **Docstrings:** Add for any non-trivial function
- Follow existing patterns — thin routers, stateless services, tasks in `worker/tasks.py`

```bash
# Run from backend/
uv run ruff format .
uv run ruff check .
```

### TypeScript (Frontend)

- **TypeScript strict mode** is enabled — no `any` types without justification
- Components must be in `frontend/app/components/`
- Use existing CSS custom properties (`--green-primary`, `--text-primary`) from `globals.css`
- Match the existing dark navy + emerald green design system

### JavaScript (Extension)

- No build step — plain ES2020+ JavaScript
- Follow the existing message-passing pattern (see `content.js` → `background.js`)
- Test on at least one real form before submitting

### Commits

- Use **present tense** ("Add feature" not "Added feature")
- Use **imperative mood** ("Fix bug" not "Fixes bug")
- Keep the first line ≤ 72 characters
- Reference issues: `fix: sort jobs by score desc — closes #42`

### Commit Message Prefixes

| Prefix | When to use |
|--------|------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `test:` | Adding tests |
| `refactor:` | Code restructure without behavior change |
| `chore:` | Build, config, tooling |
| `style:` | CSS / formatting (no logic change) |

---


## Pull Request Checklist

Before submitting your PR, make sure:

- [ ] I have read and followed this CONTRIBUTING guide
- [ ] My branch is based on the latest `main`
- [ ] My PR is linked to a claimed issue
- [ ] I have tested my changes locally
- [ ] My code follows the existing style
- [ ] I have updated documentation if the change affects setup or APIs
- [ ] I have not committed `node_modules/`, `.env`, or build artifacts

---

## 🆘 Getting Help

- **Open a Discussion** — for questions about architecture or approach before starting a large feature
- **Comment on the issue** — if you're stuck, ask there so others can help too
- **Check `backend/docs/log.md`** — detailed engineering decisions that explain *why* things are done a certain way
- **Check `http://localhost:8000/docs`** — interactive API documentation when the backend is running
- **Read the Architecture doc** — [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

We are a welcoming community. No question is too small — please ask! 🌱

---

## 📝 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
