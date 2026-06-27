from pydantic import BaseModel


class JobMatch(BaseModel):
	"""Claude's verdict on how well one job fits the CV."""
	score: int        # 0-100, where 100 is a perfect match
	explanation: str  # one or two sentences on why


class Match(BaseModel):
	"""A job plus its score: the shape the API returns to the frontend."""
	title: str
	company: str | None
	location: str | None
	url: str | None
	score: int
	explanation: str


class Company(BaseModel):
	"""A Codam-intern company: intern count, recency, and referral contacts (intraIDs)."""
	name: str
	intern_count: int
	latest_start: str
	referrals: list[str]
