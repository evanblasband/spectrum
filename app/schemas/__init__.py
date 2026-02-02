"""Request and response schemas (DTOs)."""

from app.schemas.requests import (
    AnalyzeArticleRequest,
    AnalyzeTextRequest,
    CompareArticlesRequest,
    FindRelatedRequest,
    FullAnalysisRequest,
)
from app.schemas.responses import (
    AnalysisResponse,
    ComparisonResponse,
    ErrorResponse,
    FullAnalysisResponse,
    HealthResponse,
    RelatedArticlePreview,
    RelatedArticlesResponse,
)

__all__ = [
    # Requests
    "AnalyzeArticleRequest",
    "AnalyzeTextRequest",
    "FindRelatedRequest",
    "CompareArticlesRequest",
    "FullAnalysisRequest",
    # Responses
    "AnalysisResponse",
    "RelatedArticlePreview",
    "RelatedArticlesResponse",
    "ComparisonResponse",
    "FullAnalysisResponse",
    "HealthResponse",
    "ErrorResponse",
]
