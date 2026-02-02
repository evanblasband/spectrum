"""Use case for comparing multiple articles."""

import logging
from typing import Optional

from app.core.entities.analysis import ArticleAnalysis, PointComparison
from app.core.entities.comparison import ArticleComparisonPair, MultiArticleComparison
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.cache import CacheInterface
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase

logger = logging.getLogger(__name__)


class CompareArticlesUseCase:
    """Use case for comparing multiple articles."""

    def __init__(
        self,
        analyze_use_case: AnalyzeArticleUseCase,
        ai_provider: AIProviderInterface,
        cache: Optional[CacheInterface] = None,
    ):
        self.analyze = analyze_use_case
        self.ai = ai_provider
        self.cache = cache

    async def execute(
        self,
        urls: list[str],
        comparison_depth: str = "full",
    ) -> MultiArticleComparison:
        """
        Compare multiple articles.

        Args:
            urls: List of article URLs to compare
            comparison_depth: "quick", "full", or "deep"

        Returns:
            MultiArticleComparison with analysis and comparisons
        """
        if len(urls) < 2:
            raise ValueError("At least 2 URLs are required for comparison")

        # Analyze all articles
        logger.info(f"Analyzing {len(urls)} articles for comparison")
        analyses: list[ArticleAnalysis] = []
        for url in urls:
            analysis = await self.analyze.execute(url, include_points=True)
            analyses.append(analysis)

        # Build leaning spectrum
        leaning_spectrum = {a.article_id: a.political_leaning.score for a in analyses}

        # Perform pairwise comparisons
        pairwise: list[ArticleComparisonPair] = []
        for i, a in enumerate(analyses):
            for b in analyses[i + 1 :]:
                comparison = await self._compare_pair(a, b, comparison_depth)
                pairwise.append(comparison)

        # Find consensus and contested points
        consensus, contested = self._find_consensus_contested(pairwise)

        # Generate overall summary
        summary = self._generate_summary(analyses, pairwise)

        return MultiArticleComparison(
            articles=analyses,
            pairwise_comparisons=pairwise,
            leaning_spectrum=leaning_spectrum,
            consensus_points=consensus,
            contested_points=contested,
            overall_summary=summary,
        )

    async def _compare_pair(
        self,
        a: ArticleAnalysis,
        b: ArticleAnalysis,
        depth: str,
    ) -> ArticleComparisonPair:
        """Compare two articles."""
        # Calculate leaning difference
        leaning_diff = abs(a.political_leaning.score - b.political_leaning.score)
        leaning_summary = self._summarize_leaning_difference(
            a.political_leaning.score, b.political_leaning.score
        )

        # Find shared and unique topics
        topics_a = set([a.topics.primary_topic] + a.topics.secondary_topics)
        topics_b = set([b.topics.primary_topic] + b.topics.secondary_topics)
        shared = list(topics_a & topics_b)
        unique_a = list(topics_a - topics_b)
        unique_b = list(topics_b - topics_a)

        # Compare key points if depth allows
        agreements: list[PointComparison] = []
        disagreements: list[PointComparison] = []

        if depth in ["full", "deep"] and a.key_points and b.key_points:
            comparisons = await self.ai.compare_points(
                a.key_points,
                b.key_points,
                f"{a.article_title} ({a.source_name})",
                f"{b.article_title} ({b.source_name})",
            )

            for c in comparisons:
                c.article_a_id = a.article_id
                c.article_b_id = b.article_id
                if c.relationship == "agrees":
                    agreements.append(c)
                elif c.relationship == "disagrees":
                    disagreements.append(c)

        return ArticleComparisonPair(
            article_a_id=a.article_id,
            article_b_id=b.article_id,
            leaning_difference=leaning_diff,
            leaning_summary=leaning_summary,
            shared_topics=shared,
            unique_topics_a=unique_a,
            unique_topics_b=unique_b,
            agreements=agreements,
            disagreements=disagreements,
        )

    def _summarize_leaning_difference(self, score_a: float, score_b: float) -> str:
        """Generate summary of leaning difference."""
        diff = abs(score_a - score_b)
        if diff < 0.2:
            return "Both articles have similar political leanings."
        elif diff < 0.5:
            return "The articles show moderate differences in political perspective."
        else:
            return "The articles come from significantly different political perspectives."

    def _find_consensus_contested(
        self, pairwise: list[ArticleComparisonPair]
    ) -> tuple[list[str], list[str]]:
        """Find consensus and contested points across all comparisons."""
        consensus: list[str] = []
        contested: list[str] = []

        for pair in pairwise:
            for agreement in pair.agreements:
                consensus.append(agreement.explanation)
            for disagreement in pair.disagreements:
                contested.append(disagreement.explanation)

        return consensus[:5], contested[:5]  # Limit to top 5

    def _generate_summary(
        self,
        analyses: list[ArticleAnalysis],
        pairwise: list[ArticleComparisonPair],
    ) -> str:
        """Generate overall comparison summary."""
        scores = [a.political_leaning.score for a in analyses]
        min_score, max_score = min(scores), max(scores)
        spread = max_score - min_score

        sources = [a.source_name for a in analyses]
        source_list = ", ".join(sources[:-1]) + f" and {sources[-1]}"

        if spread < 0.3:
            return f"The articles from {source_list} share similar political perspectives with minimal divergence in their coverage."
        elif spread < 0.6:
            return f"The articles from {source_list} show moderate differences in political framing, offering somewhat different perspectives on the topic."
        else:
            return f"The articles from {source_list} represent significantly different political viewpoints, providing diverse coverage of the topic."
