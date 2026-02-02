"""Analysis result models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class PoliticalLeaning(BaseModel):
    """Political leaning analysis result."""

    score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="-1=far left, 0=center, 1=far right",
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Explanation of the score")

    # Detailed breakdown
    economic_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    social_score: Optional[float] = Field(None, ge=-1.0, le=1.0)


class TopicAnalysis(BaseModel):
    """Topic and keyword extraction."""

    primary_topic: str
    secondary_topics: list[str] = []
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = []  # Named entities (people, organizations)


class ArticlePoint(BaseModel):
    """A key point/claim made in an article."""

    id: str
    statement: str
    supporting_quote: Optional[str] = None
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")


class PointComparison(BaseModel):
    """Comparison between points from different articles."""

    point_a: ArticlePoint
    point_b: ArticlePoint
    article_a_id: str
    article_b_id: str
    relationship: str = Field(..., pattern="^(agrees|disagrees|related|unrelated)$")
    explanation: str


class ArticleAnalysis(BaseModel):
    """Complete analysis result for an article."""

    article_id: str
    article_url: HttpUrl
    article_title: str
    source_name: str

    political_leaning: PoliticalLeaning
    topics: TopicAnalysis
    key_points: list[ArticlePoint]

    analyzed_at: datetime
    ai_provider: str
    cached: bool = False
