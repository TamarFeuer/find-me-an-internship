from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from app.cv import extract_pdf_text
from app.models import Company, Match
from app.adzuna import fetch_jobs
from app.companies import DATA_FILE, load_companies
from app.scoring import rank_jobs

app = FastAPI(title="find-me-an-internship")


@app.post("/matches", response_model=list[Match])
async def get_matches(
	cv: UploadFile = File(...),
	what: str = Form("software developer"),
	where: str = Form("amsterdam"),
	what_exclude: str = Form("senior"),
):
	"""Score an uploaded CV (PDF) against live job listings, ranked best-match first."""
	cv_text = extract_pdf_text(await cv.read())
	# A scanned/image-only PDF yields no text; fail clearly instead of scoring an empty CV.
	if not cv_text.strip():
		raise HTTPException(
			status_code=400,
			detail="Couldn't read any text from that PDF. It may be a scanned image. Please upload a text-based PDF.",
		)
	jobs = fetch_jobs(what=what, where=where, what_exclude=what_exclude).get("results", [])
	ranked = await rank_jobs(cv_text, jobs)

	# Shape each result into just the fields the frontend needs (not the whole Adzuna blob).
	return [
		Match(
			title=job.get("title", ""),
			company=job.get("company", {}).get("display_name"),
			location=job.get("location", {}).get("display_name"),
			url=job.get("redirect_url"),
			score=match.score,
			explanation=match.explanation,
		)
		for match, job in ranked
	]


@app.get("/companies", response_model=list[Company])
def get_companies():
	"""Companies ranked by intern count, with referral contacts (reads a local CSV - no API calls)."""
	if not DATA_FILE.exists():
		raise HTTPException(
			status_code=404,
			detail="No company data found. Add backend/data/intern_companies.csv (copy intern_companies.example.csv).",
		)
	return load_companies()


# Serve the frontend (index.html, app.js, styles.css) at the root, same-origin
# with the API so the browser doesn't need CORS. Defined after /matches so the
# API route still wins for that path.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
