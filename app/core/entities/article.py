"""Article domain model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ArticleSource(BaseModel):
    """Metadata about article source."""

    name: str
    domain: str
    known_bias: Optional[float] = None  # Pre-known bias if available


class Article(BaseModel):
    """Core article entity."""

    id: str = Field(..., description="Unique identifier (hash of URL)")
    url: HttpUrl
    title: str
    content: str
    source: ArticleSource
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    word_count: int
    fetched_at: datetime
