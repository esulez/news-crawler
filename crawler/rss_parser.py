"""RSS feed parser for fetching articles."""

import feedparser
from typing import List, Optional, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
from storage.database import Article
from crawler.site_config import SiteConfig
import requests


class RSSParser:
    """Parse RSS feeds to extract articles."""
    
    def __init__(self, user_agent: str = "NewsCrawler/1.0", timeout: int = 10):
        """Initialize the RSS parser."""
        self.user_agent = user_agent
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
    
    def parse_feed(self, feed_url: str, site_config: SiteConfig) -> List[Article]:
        """Parse an RSS feed and extract articles."""
        try:
            # Fetch the feed
            response = self.session.get(feed_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse the feed
            feed = feedparser.parse(response.content)
            
            articles = []
            for entry in feed.entries:
                article = self._entry_to_article(entry, site_config)
                if article:
                    articles.append(article)
            
            return articles
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
            return []
    
    def _entry_to_article(self, entry: Dict[str, Any], site_config: SiteConfig) -> Optional[Article]:
        """Convert an RSS entry to an Article object."""
        try:
            # Extract title
            title = entry.get('title', '')
            if not title:
                return None
            
            # Extract URL
            url = entry.get('link', '')
            if not url:
                # Try to find link in other fields
                for field in ['links', 'id']:
                    if isinstance(entry.get(field), list):
                        for link in entry[field]:
                            if isinstance(link, dict) and link.get('rel') == 'alternate':
                                url = link.get('href', '')
                                break
                    elif isinstance(entry.get(field), str):
                        url = entry[field]
            
            if not url:
                return None
            
            # Extract summary/description
            summary = ''
            for field in site_config.rss_summary_field.split(', '):
                summary = entry.get(field.strip(), '')
                if summary:
                    break
            
            # Extract content
            content = ''
            for field in site_config.rss_content_field.split(', '):
                content = entry.get(field.strip(), '')
                if content:
                    break
            
            # If no content, use summary
            if not content:
                content = summary
            
            # Extract date
            published_at = None
            for field in site_config.rss_date_field.split(', '):
                date_str = entry.get(field.strip(), '')
                if date_str:
                    try:
                        published_at = date_parser.parse(date_str)
                        break
                    except:
                        continue
            
            # Extract author
            author = entry.get('author', '') or entry.get('dc_creator', '')
            if isinstance(author, dict):
                author = author.get('name', '')
            
            # Create article
            article = Article(
                title=title.strip(),
                url=url.strip(),
                summary=summary.strip() if summary else '',
                content=content.strip() if content else '',
                source=site_config.name,
                category=site_config.category,
                published_at=published_at,
                author=author.strip() if author else '',
            )
            
            return article
        except Exception as e:
            print(f"Error converting entry to article: {e}")
            return None
    
    def parse_multiple_feeds(self, site_configs: List[SiteConfig]) -> List[Article]:
        """Parse multiple RSS feeds from different sites."""
        all_articles = []
        for config in site_configs:
            if config.rss_feed and config.use_rss:
                articles = self.parse_feed(config.rss_feed, config)
                all_articles.extend(articles)
        return all_articles
