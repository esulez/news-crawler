"""Configuration for news websites."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import yaml
import os


@dataclass
class SiteConfig:
    """Configuration for a single news website."""
    name: str
    url: str
    rss_feed: Optional[str] = None
    article_selector: str = "article"
    title_selector: str = "h1, h2, h3"
    summary_selector: str = "p"
    content_selector: str = "div.article-content, article"
    date_selector: str = "time, .date"
    link_selector: str = "a"
    author_selector: str = ".author, .byline"
    image_selector: str = "img, .thumbnail"
    category: str = "tech"
    use_rss: bool = True
    use_scraping: bool = True
    
    # RSS-specific settings
    rss_title_field: str = "title"
    rss_summary_field: str = "description, summary"
    rss_content_field: str = "content:encoded"
    rss_date_field: str = "pubDate, published"
    rss_link_field: str = "link"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'url': self.url,
            'rss_feed': self.rss_feed,
            'article_selector': self.article_selector,
            'title_selector': self.title_selector,
            'summary_selector': self.summary_selector,
            'content_selector': self.content_selector,
            'date_selector': self.date_selector,
            'link_selector': self.link_selector,
            'author_selector': self.author_selector,
            'image_selector': self.image_selector,
            'category': self.category,
            'use_rss': self.use_rss,
            'use_scraping': self.use_scraping,
        }


class SiteConfigLoader:
    """Load site configurations from YAML or create defaults."""
    
    DEFAULT_CONFIG = {
        'sites': [
            {
                'name': 'TechCrunch',
                'url': 'https://techcrunch.com',
                'rss_feed': 'https://techcrunch.com/feed/',
                'category': 'tech',
            },
            {
                'name': 'The Verge',
                'url': 'https://www.theverge.com',
                'rss_feed': 'https://www.theverge.com/rss/index.xml',
                'category': 'tech',
            },
            {
                'name': 'Ars Technica',
                'url': 'https://arstechnica.com',
                'rss_feed': 'https://arstechnica.com/feed/',
                'category': 'tech',
            },
            {
                'name': 'Wired',
                'url': 'https://www.wired.com',
                'rss_feed': 'https://www.wired.com/feed/rss',
                'category': 'tech',
            },
            {
                'name': 'BBC Technology',
                'url': 'https://www.bbc.com/news/technology',
                'rss_feed': 'http://feeds.bbci.co.uk/news/technology/rss.xml',
                'category': 'tech',
            },
            {
                'name': 'Hacker News',
                'url': 'https://news.ycombinator.com',
                'rss_feed': 'https://hnrss.org/newest',
                'category': 'tech',
            },
        ],
        'crawler': {
            'user_agent': 'NewsCrawler/1.0',
            'request_timeout': 10,
            'max_articles_per_site': 50,
            'crawl_interval_hours': 1,
        },
    }
    
    @classmethod
    def load_from_file(cls, config_path: str) -> List[SiteConfig]:
        """Load site configurations from a YAML file."""
        if not os.path.exists(config_path):
            return cls.create_default_configs()
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        sites = []
        for site_data in config.get('sites', []):
            sites.append(SiteConfig(**site_data))
        
        return sites
    
    @classmethod
    def create_default_configs(cls) -> List[SiteConfig]:
        """Create default site configurations."""
        return [SiteConfig(**site) for site in cls.DEFAULT_CONFIG['sites']]
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> List[SiteConfig]:
        """Load configurations from file or use defaults."""
        if config_path:
            return cls.load_from_file(config_path)
        return cls.create_default_configs()
