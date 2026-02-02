"""Article analysis endpoints."""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.interfaces.article_fetcher import FetchError, ParseError
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.use_cases.find_related import FindRelatedUseCase
from app.dependencies import get_analyze_use_case, get_find_related_use_case
from app.schemas.requests import AnalyzeArticleRequest, FindRelatedRequest
from app.schemas.responses import (
    AnalysisResponse,
    RelatedArticlePreview,
    RelatedArticlesResponse,
)

router = APIRouter(prefix="/articles", tags=["Articles"])
logger = structlog.get_logger()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_article(
    request: AnalyzeArticleRequest,
    use_case: AnalyzeArticleUseCase = Depends(get_analyze_use_case),
) -> AnalysisResponse:
    """Analyze the political leaning of an article.

    - Fetches article content from URL
    - Analyzes political bias on -1 (far left) to 1 (far right) spectrum
    - Extracts topics, keywords, and named entities
    - Extracts key points/claims (if include_points=true)
    - Results are cached for 24 hours

    Returns 422 for validation errors, 503 for external service failures.
    """
    start_time = datetime.utcnow()
    log = logger.bind(url=str(request.url))

    try:
        log.info("starting_analysis")

        analysis = await use_case.execute(
            url=str(request.url),
            force_refresh=request.force_refresh,
            include_points=request.include_points,
        )

        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        log.info(
            "analysis_complete",
            score=analysis.political_leaning.score,
            cached=analysis.cached,
            processing_time_ms=processing_time,
        )

        return AnalysisResponse(
            success=True,
            data=analysis,
            cached=analysis.cached,
            processing_time_ms=processing_time,
        )

    except FetchError as e:
        log.warning("fetch_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not fetch article: {e}",
        )

    except ParseError as e:
        log.warning("parse_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract article content: {e}",
        )

    except Exception as e:
        log.error("analysis_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Analysis failed: {str(e)}",
        )


@router.post("/related", response_model=RelatedArticlesResponse)
async def find_related_articles(
    request: FindRelatedRequest,
    use_case: FindRelatedUseCase = Depends(get_find_related_use_case),
) -> RelatedArticlesResponse:
    """Find related articles on the same topic.

    Provide one of:
    - url: Analyzes article and uses extracted keywords
    - keywords: Direct search keywords
    - topic: Topic/category to search

    If analyze_results=true, runs political analysis on found articles.
    """
    log = logger.bind(
        url=str(request.url) if request.url else None,
        keywords=request.keywords,
        topic=request.topic,
    )

    try:
        log.info("finding_related")

        result = await use_case.execute(
            url=str(request.url) if request.url else None,
            keywords=request.keywords,
            topic=request.topic,
            limit=request.limit,
            days_back=request.days_back,
            analyze_results=request.analyze_results,
        )

        # Convert to response format
        related_previews = [
            RelatedArticlePreview(
                url=article.url,
                title=article.title,
                source=article.source,
                published_at=article.published_at,
                snippet=article.snippet,
            )
            for article in result.get("related_articles", [])
        ]

        log.info("found_related", count=len(related_previews))

        return RelatedArticlesResponse(
            success=True,
            original_analysis=result.get("original_analysis"),
            search_keywords=result.get("search_keywords", []),
            articles=related_previews,
            analyses=result.get("related_analyses", []),
            total_found=len(related_previews),
        )

    except ValueError as e:
        log.warning("validation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        log.error("find_related_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to find related articles: {str(e)}",
        )
