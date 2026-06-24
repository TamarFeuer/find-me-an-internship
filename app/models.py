from pydantic import BaseModel


class JobMatch(BaseModel):
    """Claude's verdict on how well one job fits the CV."""
    score: int        # 0-100, where 100 is a perfect match
    explanation: str  # one or two sentences on why
