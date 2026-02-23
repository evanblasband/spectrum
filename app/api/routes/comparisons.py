"""Article comparison endpoints."""

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_analyze_use_case, get_ai_provider, get_cache
from app.api.middleware.rate_limit import limiter, COMPARE_LIMIT
from app.core.entities.comparison import MultiArticleComparison
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.cache import CacheInterface
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.use_cases.compare_articles import CompareArticlesUseCase
from app.schemas.requests import CompareArticlesRequest

router = APIRouter(prefix="/comparisons", tags=["Comparisons"])
logger = logging.getLogger(__name__)


def get_compare_use_case(
    analyze: AnalyzeArticleUseCase = Depends(get_analyze_use_case),
    ai_provider: AIProviderInterface = Depends(get_ai_provider),
    cache: Optional[CacheInterface] = Depends(get_cache),
) -> CompareArticlesUseCase:
    """Assemble compare articles use case with dependencies."""
    return CompareArticlesUseCase(
        analyze_use_case=analyze,
        ai_provider=ai_provider,
        cache=cache,
    )


@router.post("", response_model=MultiArticleComparison)
@limiter.limit(COMPARE_LIMIT)
async def compare_articles(
    body: CompareArticlesRequest,
    request: Request,  # Required for rate limiter - must be named 'request'
    use_case: CompareArticlesUseCase = Depends(get_compare_use_case),
) -> MultiArticleComparison:
    """
    Compare multiple articles.

    - Analyzes each article's political leaning
    - Finds shared and unique topics
    - Identifies agreements and disagreements between articles
    - Provides overall comparison summary
    """
    start_time = time.time()

    try:
        comparison = await use_case.execute(
            urls=[str(url) for url in body.article_urls],
            comparison_depth=body.comparison_depth,
        )

        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"Comparison completed in {processing_time}ms")

        return comparison

    except ValueError as e:
        logger.warning(f"Invalid comparison request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Comparison failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Comparison failed: {str(e)}",
        )
