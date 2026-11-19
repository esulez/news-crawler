"""News Crawler - A web crawler for aggregating and deduplicating news articles."""

from .crawler import NewsCrawler
from .storage import Database
from .utils import Deduplicator

__version__ = "1.0.0"
__all__ = ["NewsCrawler", "Database", "Deduplicator"]
