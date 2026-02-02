"""Analysis result domain entities."""

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
    economic_score: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Economic policy stance",
    )
    social_score: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Social policy stance",
    )

    @property
    def label(self) -> str:
        """Human-readable label for the score."""
        if self.score <= -0.6:
            return "Far Left"
        elif self.score <= -0.2:
            return "Left"
        elif self.score <= 0.2:
            return "Center"
        elif self.score <= 0.6:
            return "Right"
        else:
            return "Far Right"


class TopicAnalysis(BaseModel):
    """Topic and keyword extraction result."""

    primary_topic: str
    secondary_topics: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(..., max_length=10)
    entities: list[str] = Field(
        default_factory=list,
        description="Named entities (people, organizations)",
    )


class ArticlePoint(BaseModel):
    """A key point/claim made in an article."""

    id: str
    statement: str
    supporting_quote: Optional[str] = None
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")


class ArticleAnalysis(BaseModel):
    """Complete analysis result for an article."""

    article_id: str
    article_url: HttpUrl
    article_title: str
    source_name: str

    political_leaning: PoliticalLeaning
    topics: TopicAnalysis
    key_points: list[ArticlePoint] = Field(default_factory=list)

    analyzed_at: datetime
    ai_provider: str
    cached: bool = False

    model_config = {"from_attributes": True}
