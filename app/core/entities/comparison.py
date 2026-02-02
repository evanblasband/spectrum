"""Comparison domain entities."""

from typing import Optional

from pydantic import BaseModel, Field

from app.core.entities.analysis import ArticleAnalysis, ArticlePoint


class PointComparison(BaseModel):
    """Comparison between points from different articles."""

    point_a: ArticlePoint
    point_b: ArticlePoint
    article_a_id: str
    article_b_id: str
    relationship: str = Field(
        ...,
        pattern="^(agrees|disagrees|related|unrelated)$",
    )
    explanation: str


class ArticleComparison(BaseModel):
    """Full comparison between two articles."""

    article_a_id: str
    article_b_id: str
    article_a_title: str
    article_b_title: str

    # Leaning comparison
    leaning_difference: float = Field(
        ...,
        description="Absolute difference in political leaning scores",
    )
    leaning_summary: str

    # Topic overlap
    shared_topics: list[str] = Field(default_factory=list)
    unique_topics_a: list[str] = Field(default_factory=list)
    unique_topics_b: list[str] = Field(default_factory=list)

    # Point comparisons
    agreements: list[PointComparison] = Field(default_factory=list)
    disagreements: list[PointComparison] = Field(default_factory=list)

    overall_summary: str


class MultiArticleComparison(BaseModel):
    """Comparison across multiple articles."""

    articles: list[ArticleAnalysis]
    pairwise_comparisons: list[ArticleComparison] = Field(default_factory=list)

    # Aggregate insights
    leaning_spectrum: dict[str, float] = Field(
        default_factory=dict,
        description="article_id -> political leaning score",
    )
    consensus_points: list[str] = Field(
        default_factory=list,
        description="Points most articles agree on",
    )
    contested_points: list[str] = Field(
        default_factory=list,
        description="Points where articles disagree",
    )
    overall_summary: Optional[str] = None
