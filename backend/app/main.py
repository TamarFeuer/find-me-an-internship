from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.models import Match
from app.adzuna import fetch_jobs
from app.scoring import load_cv, rank_jobs

app = FastAPI(title="find-me-an-internship")


@app.get("/matches", response_model=list[Match])
def get_matches():
	"""Fetch jobs, score each against the CV, return them ranked best-match first."""
	cv_text = load_cv()
	jobs = fetch_jobs().get("results", [])
	ranked = rank_jobs(cv_text, jobs)

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


# Serve the frontend (index.html, app.js, styles.css) at the root, same-origin
# with the API so the browser doesn't need CORS. Defined after /matches so the
# API route still wins for that path.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
