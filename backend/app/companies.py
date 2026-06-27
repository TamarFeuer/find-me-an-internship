import csv
import re
from collections import defaultdict
from pathlib import Path

# CSV of companies known to hire interns (gitignored - contains real referral handles).
# See intern_companies.example.csv for the expected format.
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "intern_companies.csv"

# Strip legal suffixes and location prefixes so name variants merge into one company,
# e.g. "TomTom International B.V." and "TomTom International BV" become the same key.
_SUFFIXES = re.compile(
    r"\b(b\.?\s?v\.?|n\.?\s?v\.?|gmbh|inc|llc|ltd|corp|holding|u\.?a\.?|e\.?\s?v\.?)\b\.?",
    re.IGNORECASE,
)
_PREFIX = re.compile(r"^nl\d+\s+", re.IGNORECASE)  # drop "NL11 ", "NL82 " style prefixes

# The referral column may be named "referral" (this project's format) or "intraID"
# (e.g. a Codam internship export), so accept either - the raw file imports unedited.
_REFERRAL_KEYS = ("referral", "intraID")


def _referral(row):
    for key in _REFERRAL_KEYS:
        value = row.get(key)
        if value:
            return value
    return ""


def _normalize(name):
    name = _PREFIX.sub("", name)
    name = _SUFFIXES.sub("", name)
    name = re.sub(r"[^\w\s]", " ", name)   # punctuation -> space
    name = re.sub(r"\s+", " ", name).strip().lower()
    return name


def load_companies():
    """Read the Codam interns CSV and aggregate it into a ranked company directory."""
    groups = defaultdict(lambda: {"display": None, "interns": [], "starts": []})

    with open(DATA_FILE, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            raw = row["company_name"].strip()
            key = _normalize(raw)
            if not key:
                continue
            group = groups[key]
            group["interns"].append(_referral(row))       # referral contact (referral/intraID)
            group["starts"].append(row["start_at"][:10])  # YYYY-MM-DD
            # Keep the shortest name variant as the display name.
            if group["display"] is None or len(raw) < len(group["display"]):
                group["display"] = raw

    companies = [
        {
            "name": group["display"],
            "intern_count": len(group["interns"]),
            "latest_start": max(group["starts"]),
            "referrals": sorted(set(group["interns"])),
        }
        for group in groups.values()
    ]
    # Most intern-friendly first (highest count), then most recent.
    companies.sort(key=lambda c: (c["intern_count"], c["latest_start"]), reverse=True)
    return companies
