"""Use case for comparing multiple articles."""

import asyncio

import structlog

from app.core.entities.analysis import ArticleAnalysis
from app.core.entities.comparison import (
    ArticleComparison,
    MultiArticleComparison,
    PointComparison,
)
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.cache import CacheInterface
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.services.cache.cache_keys import CacheKeys

logger = structlog.get_logger()


class CompareArticlesUseCase:
    """Use case for comparing multiple articles.

    Orchestrates:
    1. Analyzing all articles
    2. Comparing political leanings
    3. Finding topic overlaps
    4. Comparing key points for agreements/disagreements
    5. Generating overall comparison summary
    """

    def __init__(
        self,
        ai_provider: AIProviderInterface,
        analyze_use_case: AnalyzeArticleUseCase,
        cache: CacheInterface,
    ):
        self.ai = ai_provider
        self.analyze = analyze_use_case
        self.cache = cache

    async def execute(
        self,
        urls: list[str],
        comparison_depth: str = "full",
    ) -> MultiArticleComparison:
        """Compare multiple articles.

        Args:
            urls: List of article URLs to compare (2-5 articles)
            comparison_depth: "quick" (leaning only), "full" (with points), "deep" (detailed)

        Returns:
            MultiArticleComparison with analyses and comparisons
        """
        if len(urls) < 2:
            raise ValueError("Need at least 2 articles to compare")
        if len(urls) > 5:
            raise ValueError("Maximum 5 articles for comparison")

        log = logger.bind(article_count=len(urls), depth=comparison_depth)

        # Check cache
        cache_key = CacheKeys.comparison(urls)
        cached = await self.cache.get(cache_key)
        if cached:
            log.info("cache_hit", cache_key=cache_key)
            return cached

        # Analyze all articles in parallel
        log.info("analyzing_articles")
        include_points = comparison_depth in ("full", "deep")

        analyses = await asyncio.gather(
            *[
                self.analyze.execute(url, include_points=include_points)
                for url in urls
            ],
            return_exceptions=True,
        )

        # Filter out failures
        valid_analyses: list[ArticleAnalysis] = []
        for i, result in enumerate(analyses):
            if isinstance(result, Exception):
                log.warning("analysis_failed", url=urls[i], error=str(result))
            else:
                valid_analyses.append(result)

        if len(valid_analyses) < 2:
            raise ValueError("Need at least 2 successful analyses to compare")

        # Build leaning spectrum
        leaning_spectrum = {
            a.article_id: a.political_leaning.score
            for a in valid_analyses
        }

        # Generate pairwise comparisons
        log.info("generating_comparisons")
        pairwise = []
        for i, a in enumerate(valid_analyses):
            for b in valid_analyses[i + 1:]:
                comparison = await self._compare_pair(a, b, include_points)
                pairwise.append(comparison)

        # Find consensus and contested points
        consensus, contested = self._aggregate_points(pairwise)

        # Build result
        result = MultiArticleComparison(
            articles=valid_analyses,
            pairwise_comparisons=pairwise,
            leaning_spectrum=leaning_spectrum,
            consensus_points=consensus,
            contested_points=contested,
            overall_summary=self._generate_summary(valid_analyses, pairwise),
        )

        # Cache result
        await self.cache.set(cache_key, result)

        log.info("comparison_complete", pairs=len(pairwise))
        return result

    async def _compare_pair(
        self,
        a: ArticleAnalysis,
        b: ArticleAnalysis,
        include_points: bool,
    ) -> ArticleComparison:
        """Compare two articles.

        Args:
            a: First article analysis
            b: Second article analysis
            include_points: Whether to compare key points

        Returns:
            ArticleComparison between the two articles
        """
        # Calculate leaning difference
        leaning_diff = abs(a.political_leaning.score - b.political_leaning.score)
        leaning_summary = self._describe_leaning_difference(
            a.political_leaning.score,
            b.political_leaning.score,
            a.source_name,
            b.source_name,
        )

        # Find topic overlaps
        topics_a = set([a.topics.primary_topic] + a.topics.secondary_topics)
        topics_b = set([b.topics.primary_topic] + b.topics.secondary_topics)

        shared = list(topics_a & topics_b)
        unique_a = list(topics_a - topics_b)
        unique_b = list(topics_b - topics_a)

        # Compare points if available
        agreements = []
        disagreements = []

        if include_points and a.key_points and b.key_points:
            comparisons = await self.ai.compare_points(
                a.key_points,
                b.key_points,
                f"{a.article_title} ({a.source_name})",
                f"{b.article_title} ({b.source_name})",
            )

            # Fill in article IDs and separate by relationship
            for c in comparisons:
                c.article_a_id = a.article_id
                c.article_b_id = b.article_id

                if c.relationship == "agrees":
                    agreements.append(c)
                elif c.relationship == "disagrees":
                    disagreements.append(c)

        return ArticleComparison(
            article_a_id=a.article_id,
            article_b_id=b.article_id,
            article_a_title=a.article_title,
            article_b_title=b.article_title,
            leaning_difference=leaning_diff,
            leaning_summary=leaning_summary,
            shared_topics=shared,
            unique_topics_a=unique_a,
            unique_topics_b=unique_b,
            agreements=agreements,
            disagreements=disagreements,
            overall_summary=self._generate_pair_summary(
                a, b, len(agreements), len(disagreements)
            ),
        )

    def _describe_leaning_difference(
        self,
        score_a: float,
        score_b: float,
        source_a: str,
        source_b: str,
    ) -> str:
        """Generate human-readable description of leaning difference."""
        diff = abs(score_a - score_b)

        if diff < 0.2:
            return f"{source_a} and {source_b} have similar political leanings."
        elif diff < 0.5:
            return f"{source_a} and {source_b} have moderately different perspectives."
        elif diff < 0.8:
            return f"{source_a} and {source_b} present notably different viewpoints."
        else:
            return f"{source_a} and {source_b} represent opposing ends of the political spectrum."

    def _generate_pair_summary(
        self,
        a: ArticleAnalysis,
        b: ArticleAnalysis,
        agreement_count: int,
        disagreement_count: int,
    ) -> str:
        """Generate summary for a pair comparison."""
        parts = []

        # Leaning summary
        diff = abs(a.political_leaning.score - b.political_leaning.score)
        if diff < 0.3:
            parts.append("Both articles share a similar political perspective")
        else:
            parts.append(
                f"The articles differ in political leaning "
                f"({a.political_leaning.label} vs {b.political_leaning.label})"
            )

        # Points summary
        if agreement_count > 0 or disagreement_count > 0:
            if agreement_count > disagreement_count:
                parts.append(f"with more points of agreement ({agreement_count}) than disagreement ({disagreement_count})")
            elif disagreement_count > agreement_count:
                parts.append(f"with more points of disagreement ({disagreement_count}) than agreement ({agreement_count})")
            else:
                parts.append(f"with equal points of agreement and disagreement ({agreement_count} each)")

        return ". ".join(parts) + "."

    def _aggregate_points(
        self,
        pairwise: list[ArticleComparison],
    ) -> tuple[list[str], list[str]]:
        """Aggregate points across all comparisons.

        Returns:
            Tuple of (consensus_points, contested_points)
        """
        # Track which points appear in agreements vs disagreements
        agreed_statements = []
        disagreed_statements = []

        for comparison in pairwise:
            for agreement in comparison.agreements:
                agreed_statements.append(agreement.point_a.statement)

            for disagreement in comparison.disagreements:
                disagreed_statements.append(
                    f"{disagreement.point_a.statement} vs {disagreement.point_b.statement}"
                )

        # Deduplicate (simple approach - could use similarity matching)
        consensus = list(set(agreed_statements))[:5]
        contested = list(set(disagreed_statements))[:5]

        return consensus, contested

    def _generate_summary(
        self,
        analyses: list[ArticleAnalysis],
        pairwise: list[ArticleComparison],
    ) -> str:
        """Generate overall comparison summary."""
        # Calculate average leaning spread
        scores = [a.political_leaning.score for a in analyses]
        spread = max(scores) - min(scores)

        # Count total agreements/disagreements
        total_agree = sum(len(c.agreements) for c in pairwise)
        total_disagree = sum(len(c.disagreements) for c in pairwise)

        parts = []

        # Leaning spread
        if spread < 0.3:
            parts.append(f"All {len(analyses)} articles share similar political perspectives")
        elif spread < 0.6:
            parts.append(f"The {len(analyses)} articles show moderate political diversity")
        else:
            parts.append(f"The {len(analyses)} articles span a wide range of political viewpoints")

        # Point summary
        if total_agree + total_disagree > 0:
            if total_agree > total_disagree:
                parts.append("with more points of agreement than disagreement")
            elif total_disagree > total_agree:
                parts.append("with more contested points than consensus")
            else:
                parts.append("with a balance of agreed and contested points")

        return ". ".join(parts) + "."
