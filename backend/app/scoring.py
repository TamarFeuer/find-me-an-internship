import os

import anthropic
from dotenv import load_dotenv

from app.models import JobMatch

# Load .env so ANTHROPIC_API_KEY and ANTHROPIC_MODEL are available.
load_dotenv()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

# Model comes from .env, but falls back to a sensible default if it's not set.
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")

INSTRUCTIONS = (
    "You score how well a job listing matches a candidate's CV. "
    "Give a score from 0 to 100 and a short, specific explanation (1-2 sentences) "
    "citing concrete overlaps or gaps.\n"
    # Grounding: stops the model inventing skills the CV doesn't actually state.
    "Base your reasoning only on skills and experience explicitly written in the CV. "
    "Do not infer or assume capabilities that are not there; if the CV doesn't mention "
    "something the job needs, treat it as a gap.\n"
    # Spread the scores so the ranking is meaningful instead of bunched together.
    "Use the full range: reserve 80+ for genuinely strong matches, 40-70 for partial "
    "fits, and below 40 for weak fits."
)


def load_cv(path="cv.txt"):
    with open(path, encoding="utf-8") as f:
        return f.read()


def score_job(cv_text, job):
    """Ask Claude to score one job against the CV. Returns a JobMatch."""
    title = job.get("title", "")
    company = job.get("company", {}).get("display_name", "")
    description = job.get("description", "")
    job_text = f"Title: {title}\nCompany: {company}\n\nDescription:\n{description}"

    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        system=[
            {"type": "text", "text": INSTRUCTIONS},
            # The CV is identical for every job, so mark it as the cacheable prefix.
            {
                "type": "text",
                "text": f"Candidate CV:\n{cv_text}",
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": f"Score this job:\n\n{job_text}"}],
        output_format=JobMatch,
    )

    # Caching diagnostic: cache_read > 0 means the CV prefix was served from cache.
    # At a short CV (< ~4096 tokens) this stays 0 on Haiku — caching is dormant.
    usage = response.usage
    print(
        f"  [tokens] full-price={usage.input_tokens} "
        f"cache-write={usage.cache_creation_input_tokens} "
        f"cache-read={usage.cache_read_input_tokens}"
    )

    return response.parsed_output  # a validated JobMatch


def rank_jobs(cv_text, jobs):
    """Score every job, return them sorted best-match first."""
    scored = [(score_job(cv_text, job), job) for job in jobs]
    scored.sort(key=lambda pair: pair[0].score, reverse=True)
    return scored


def main():
    # Local import to avoid a circular dependency at module load time.
    from app.adzuna import fetch_jobs

    cv_text = load_cv()
    jobs = fetch_jobs().get("results", [])
    ranked = rank_jobs(cv_text, jobs)

    for match, job in ranked:
        print(f"[{match.score:3}] {job.get('title', '(no title)')}")
        print(f"      {match.explanation}")


# Run with:  python -m app.scoring   (from the project root)
if __name__ == "__main__":
    main()
