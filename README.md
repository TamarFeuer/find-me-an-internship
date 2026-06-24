# find-me-an-internship

## What is this project?

An AI-powered internship matcher. You upload your CV as a PDF, the app fetches
live job listings, scores each one against your CV using a large language model,
and shows them ranked from best match to worst — each with a short explanation
of *why* it fits (or doesn't).

![Find Me an Internship — ranked job matches with fit scores and explanations](docs/app-preview.png)

How it works, end to end:

1. You upload your CV (PDF) and optionally set the role, location, and words to exclude.
2. The backend extracts the text from the PDF.
3. It fetches matching job listings from the **Adzuna** API.
4. It sends your CV plus each listing to the **Claude** API, which returns a 0–100
   fit score and a one-line explanation per job.
5. The scored jobs are ranked best-first and shown as cards in the browser.

## Tech stack

| Part | Technology |
|------|------------|
| Job listings | [Adzuna API](https://developer.adzuna.com) |
| CV scoring | [Anthropic Claude API](https://platform.claude.com) |
| Backend | Python + [FastAPI](https://fastapi.tiangolo.com) (also serves the frontend) |
| Frontend | Vanilla **TypeScript** (compiled with `tsc`), HTML, CSS |
| PDF text extraction | [pypdf](https://pypdf.readthedocs.io) |

The frontend is plain TypeScript (no framework) and is served as static files by
FastAPI, so the whole app runs from a single server with no CORS setup.

```
find-me-an-internship/
├── backend/          # FastAPI app + scoring/fetching logic
│   └── app/
├── frontend/         # vanilla TypeScript UI (compiled to dist/app.js)
└── README.md
```

## Getting started

### Prerequisites

- **Python 3.10+**
- **Node.js** (only to build the TypeScript frontend)
- An **Adzuna** API key (free — [developer.adzuna.com](https://developer.adzuna.com))
- An **Anthropic** API key ([platform.claude.com](https://platform.claude.com))

### 1. Configure environment variables

```bash
cd backend
cp .env.example .env
```

Then open `.env` and fill in your keys:

```
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-haiku-4-5
```

`.env` is gitignored, so your keys are never committed.

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Build the frontend

```bash
cd frontend
npm install
npm run build      # compiles src/app.ts -> dist/app.js
```

### 4. Run the app

```bash
cd backend
uvicorn app.main:app --reload
```

Then open **http://localhost:8000** in your browser, upload a PDF CV, and click
**Find matches**.

## Notes

- Scoring calls the Claude API once per job, so each search costs a few cents
  (with the default Haiku model). To switch to a sharper, pricier model, edit
  `ANTHROPIC_MODEL` in `.env` (a commented Sonnet line is included) and restart the server.
- The interactive API docs are available at **http://localhost:8000/docs**.
