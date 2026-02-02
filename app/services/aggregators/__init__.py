"""News aggregator implementations."""

from app.services.aggregators.gnews import GNewsAggregator
from app.services.aggregators.newsapi import NewsAPIAggregator

__all__ = ["NewsAPIAggregator", "GNewsAggregator"]
