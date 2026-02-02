"""Application use cases."""

from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.use_cases.compare_articles import CompareArticlesUseCase
from app.core.use_cases.find_related import FindRelatedUseCase

__all__ = [
    "AnalyzeArticleUseCase",
    "FindRelatedUseCase",
    "CompareArticlesUseCase",
]
