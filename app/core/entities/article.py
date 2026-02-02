"""Article domain entities."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ArticleSource(BaseModel):
    """Metadata about article source."""

    name: str
    domain: str
    known_bias: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Pre-known bias if available (-1=left, 1=right)",
    )


class Article(BaseModel):
    """Core article entity representing fetched article content."""

    id: str = Field(..., description="Unique identifier (hash of URL)")
    url: HttpUrl
    title: str
    content: str
    source: ArticleSource
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    word_count: int
    fetched_at: datetime

    @classmethod
    def generate_id(cls, url: str) -> str:
        """Generate consistent ID from URL."""
        import hashlib

        return hashlib.md5(url.encode()).hexdigest()[:12]
