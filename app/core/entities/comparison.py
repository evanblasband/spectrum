"""Comparison result models."""

from pydantic import BaseModel

from app.core.entities.analysis import ArticleAnalysis, ArticlePoint, PointComparison


class ArticleComparisonPair(BaseModel):
    """Comparison between two articles."""

    article_a_id: str
    article_b_id: str

    # Leaning comparison
    leaning_difference: float  # Absolute difference
    leaning_summary: str

    # Topic overlap
    shared_topics: list[str]
    unique_topics_a: list[str]
    unique_topics_b: list[str]

    # Point comparisons
    agreements: list[PointComparison]
    disagreements: list[PointComparison]


class MultiArticleComparison(BaseModel):
    """Comparison across multiple articles."""

    articles: list[ArticleAnalysis]
    pairwise_comparisons: list[ArticleComparisonPair]

    # Aggregate insights
    leaning_spectrum: dict[str, float]  # article_id -> score
    consensus_points: list[str]
    contested_points: list[str]
    overall_summary: str
