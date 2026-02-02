"""Article comparison endpoints."""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.use_cases.compare_articles import CompareArticlesUseCase
from app.core.use_cases.find_related import FindRelatedUseCase
from app.dependencies import get_compare_use_case, get_find_related_use_case
from app.schemas.requests import CompareArticlesRequest, FullAnalysisRequest
from app.schemas.responses import ComparisonResponse, FullAnalysisResponse

router = APIRouter(prefix="/comparisons", tags=["Comparisons"])
logger = structlog.get_logger()


@router.post("", response_model=ComparisonResponse)
async def compare_articles(
    request: CompareArticlesRequest,
    use_case: CompareArticlesUseCase = Depends(get_compare_use_case),
) -> ComparisonResponse:
    """Compare multiple articles.

    Analyzes 2-5 articles and compares:
    - Political leanings (difference and spectrum)
    - Topic overlaps and unique topics
    - Key points agreements and disagreements
    - Overall summary

    Comparison depths:
    - quick: Leaning comparison only (fastest)
    - full: Includes key point comparison (default)
    - deep: Detailed analysis with more context
    """
    start_time = datetime.utcnow()
    urls = [str(url) for url in request.article_urls]
    log = logger.bind(article_count=len(urls), depth=request.comparison_depth)

    try:
        log.info("starting_comparison")

        comparison = await use_case.execute(
            urls=urls,
            comparison_depth=request.comparison_depth,
        )

        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        log.info(
            "comparison_complete",
            articles_analyzed=len(comparison.articles),
            processing_time_ms=processing_time,
        )

        return ComparisonResponse(
            success=True,
            data=comparison,
            articles_analyzed=len(comparison.articles),
            processing_time_ms=processing_time,
        )

    except ValueError as e:
        log.warning("validation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        log.error("comparison_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Comparison failed: {str(e)}",
        )


@router.post("/full", response_model=FullAnalysisResponse)
async def full_analysis(
    request: FullAnalysisRequest,
    find_related_use_case: FindRelatedUseCase = Depends(get_find_related_use_case),
    compare_use_case: CompareArticlesUseCase = Depends(get_compare_use_case),
) -> FullAnalysisResponse:
    """Complete analysis workflow.

    1. Analyzes the primary article
    2. Finds related articles (if find_related=true)
    3. Analyzes related articles
    4. Compares all articles (if compare_all=true)

    This is a convenience endpoint that combines multiple operations.
    """
    start_time = datetime.utcnow()
    url = str(request.url)
    log = logger.bind(
        url=url,
        find_related=request.find_related,
        compare_all=request.compare_all,
    )

    try:
        log.info("starting_full_analysis")

        # Step 1 & 2: Analyze primary and find related
        related_result = await find_related_use_case.execute(
            url=url,
            limit=request.related_count,
            analyze_results=request.find_related,
        )

        primary_analysis = related_result.get("original_analysis")
        related_analyses = related_result.get("related_analyses", [])

        # Step 3: Compare if requested
        comparison = None
        if request.compare_all and related_analyses:
            all_urls = [url] + [str(a.article_url) for a in related_analyses]
            comparison = await compare_use_case.execute(
                urls=all_urls,
                comparison_depth="full",
            )

        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        log.info(
            "full_analysis_complete",
            related_count=len(related_analyses),
            has_comparison=comparison is not None,
            processing_time_ms=processing_time,
        )

        return FullAnalysisResponse(
            success=True,
            primary_article=primary_analysis,
            related_articles=related_analyses,
            comparison=comparison,
            total_processing_time_ms=processing_time,
        )

    except ValueError as e:
        log.warning("validation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        log.error("full_analysis_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Full analysis failed: {str(e)}",
        )
