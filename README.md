# CourseSync — Intelligent Knowledge Pipeline

> AI-powered course ingestion platform that transforms university course websites into NotebookLM-ready knowledge files.

## Overview

CourseSync ingests a university course from a public URL, discovers its structure, extracts its content via [Firecrawl](https://firecrawl.dev), classifies and structures that content with an LLM, and outputs clean, source-faithful, NotebookLM-ready knowledge files.

### Pipeline

```
University Course URL
   → Course Discovery (Firecrawl Map)
   → URL Classification (Deterministic heuristics)
   → Page Scraping (Firecrawl Scrape)
   → AI Structuring (LLM Provider)
   → Two-Layer Output (Source + Knowledge)
   → NotebookLM-ready Markdown exports
```

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript + Vite + Tailwind CSS v4 |
| Backend | Python + FastAPI + Pydantic |
| Web Extraction | Firecrawl API (Python SDK) |
| AI Layer | Swappable LLM Provider (Gemini / Nemotron) |
| Storage | SQLite (metadata) + Local filesystem (content) |

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Firecrawl API key ([get one here](https://firecrawl.dev))
- Gemini API key or NVIDIA NIM API key

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api/*` to the backend.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIRECRAWL_API_KEY` | Yes | Firecrawl API key |
| `LLM_PROVIDER` | Yes | `gemini` or `nemotron` |
| `GEMINI_API_KEY` | If using Gemini | Google AI API key |
| `GEMINI_MODEL` | No | Default: `gemini-2.5-flash` |
| `NEMOTRON_API_KEY` | If using Nemotron | NVIDIA NIM API key |
| `NEMOTRON_BASE_URL` | No | Default: `https://integrate.api.nvidia.com/v1` |
| `NEMOTRON_MODEL` | No | Default: `nvidia/nemotron-3.5-lightning-30b` |
| `DATABASE_URL` | No | Default: SQLite in `data/` |
| `APP_ENV` | No | `development` or `production` |

## User Workflow

1. **Add Course** — Enter course name and root URL
2. **Discover** — CourseSync maps and classifies all sub-pages
3. **Select** — Review the hierarchy tree and select pages to import
4. **Scrape** — Extract content from selected pages via Firecrawl
5. **Process** — Run AI structuring to extract concepts, definitions, quiz topics
6. **Export** — Generate NotebookLM-ready markdown files
7. **Download** — Download and import into NotebookLM

## Project Structure

```
coursesync/
├── frontend/
│   └── src/
│       ├── components/   # Reusable UI components
│       ├── pages/        # Route-level pages
│       ├── services/     # API client
│       ├── types/        # TypeScript type definitions
│       └── index.css     # Design system
├── backend/
│   └── app/
│       ├── api/routes/   # FastAPI endpoints
│       ├── core/         # Config, database, exceptions
│       ├── schemas/      # Pydantic models
│       ├── services/     # Business logic
│       │   └── llm/      # LLM provider abstraction
│       └── repositories/ # Data access layer
├── data/
│   ├── raw/              # Raw Firecrawl output
│   ├── processed/        # AI-structured content
│   └── exports/          # NotebookLM-ready files
└── docs/                 # Architecture documentation
```

## Two-Layer Output

CourseSync generates two distinct file types per module:

- **Source Layer** (`module-XX-source.md`): Cleaned original content as close to source as possible
- **Knowledge Layer** (`module-XX-knowledge.md`): AI-structured summaries, concepts, definitions, quiz topics

Both layers are independently importable into NotebookLM.

## Known Limitations

- Single-user / local-first (no multi-tenant auth)
- Authenticated LMS platforms (Canvas, Moodle) not supported yet
- No autonomous agent (planned for Phase 12)
- Equation/table extraction quality depends on Firecrawl's markdown output

## License

Private — © 2026 Tony
