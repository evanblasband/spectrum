"""Article analysis endpoints."""

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from tenacity import RetryError

from app.api.deps import get_analyze_use_case, get_find_related_use_case
from app.api.errors import raise_structured_error
from app.core.errors import ErrorCode
from app.core.interfaces.article_fetcher import ArticleFetchError
from app.services.fetchers.web_scraper import RetryableError, SUPPORTED_SITES, BLOCKED_SITES, PARTIAL_SUPPORT_SITES
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.use_cases.find_related import FindRelatedUseCase
from app.schemas.requests import AnalyzeArticleRequest, FindRelatedRequest
from app.schemas.responses import AnalysisResponse, RelatedArticlesResponse, RelatedArticlePreview

router = APIRouter(prefix="/articles", tags=["Articles"])
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_article(
    request: AnalyzeArticleRequest,
    use_case: AnalyzeArticleUseCase = Depends(get_analyze_use_case),
) -> AnalysisResponse:
    """
    Analyze the political leaning of an article.

    - Fetches article content from URL
    - Analyzes political bias on -1 (left) to 1 (right) spectrum
    - Extracts topics, keywords, and key points
    - Results are cached for 24 hours
    """
    start_time = time.time()

    try:
        analysis = await use_case.execute(
            url=str(request.url),
            force_refresh=request.force_refresh,
            include_points=request.include_points,
        )

        processing_time = int((time.time() - start_time) * 1000)

        return AnalysisResponse(
            success=True,
            data=analysis,
            cached=analysis.cached,
            processing_time_ms=processing_time,
        )

    except ArticleFetchError as e:
        logger.warning(f"Failed to fetch article: {e}")
        raise_structured_error(
            code=e.code,
            message=e.message,
            details={"url": e.url, **(e.details or {})},
        )
    except (RetryableError, RetryError) as e:
        # Retries exhausted for connection/timeout errors
        original_error = e.__cause__ if isinstance(e, RetryError) else e
        logger.warning(f"Failed to fetch article after retries: {original_error}")
        raise_structured_error(
            code=ErrorCode.NETWORK_ERROR,
            message="Could not reach the article URL after multiple attempts.",
            details={"original_error": str(original_error)},
        )
    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        raise_structured_error(
            code=ErrorCode.VALIDATION,
            message=str(e),
        )
    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        raise_structured_error(
            code=ErrorCode.AI_ERROR,
            message=f"Analysis failed: {str(e)}",
        )


@router.post("/related", response_model=RelatedArticlesResponse)
async def find_related_articles(
    request: FindRelatedRequest,
    use_case: FindRelatedUseCase | None = Depends(get_find_related_use_case),
) -> RelatedArticlesResponse:
    """
    Find related articles on the same topic.

    - Provide a URL to extract keywords from the article
    - Or provide keywords/topic directly
    - Returns up to 5 related articles from various sources
    """
    if use_case is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="News API not configured. Set NEWSAPI_KEY environment variable.",
        )

    try:
        keywords, articles = await use_case.execute(
            url=str(request.url) if request.url else None,
            keywords=request.keywords,
            topic=request.topic,
            limit=request.limit,
            days_back=request.days_back,
        )

        return RelatedArticlesResponse(
            success=True,
            original_keywords=keywords,
            articles=[
                RelatedArticlePreview(
                    url=a.url,
                    title=a.title,
                    source=a.source,
                    published_at=a.published_at,
                    snippet=a.snippet,
                )
                for a in articles
            ],
            total_found=len(articles),
        )

    except Exception as e:
        logger.exception(f"Find related failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to find related articles: {str(e)}",
        )


@router.get("/sources")
async def get_source_compatibility() -> dict:
    """
    Get list of supported and blocked news sources.

    Returns information about which news sources work with the scraper
    and which are known to block automated access.
    """
    return {
        "supported": SUPPORTED_SITES,
        "partial": PARTIAL_SUPPORT_SITES,
        "blocked": [
            {"domain": domain, "reason": reason}
            for domain, reason in BLOCKED_SITES.items()
        ],
    }
