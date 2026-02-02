"""Domain entities."""

from app.core.entities.analysis import (
    ArticleAnalysis,
    ArticlePoint,
    PoliticalLeaning,
    TopicAnalysis,
)
from app.core.entities.article import Article, ArticleSource
from app.core.entities.comparison import (
    ArticleComparison,
    MultiArticleComparison,
    PointComparison,
)

__all__ = [
    "Article",
    "ArticleSource",
    "ArticleAnalysis",
    "ArticlePoint",
    "PoliticalLeaning",
    "TopicAnalysis",
    "ArticleComparison",
    "MultiArticleComparison",
    "PointComparison",
]
