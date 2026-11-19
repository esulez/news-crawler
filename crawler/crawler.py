"""Main news crawler class."""

import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from crawler.site_config import SiteConfig, SiteConfigLoader
from crawler.rss_parser import RSSParser
from crawler.web_scraper import WebScraper
from storage.database import Database, Article
import asyncio
import concurrent.futures


class NewsCrawler:
    """Main crawler class that orchestrates fetching articles from multiple sources."""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        db_path: str = "data/news.db",
        user_agent: str = "NewsCrawler/1.0",
        timeout: int = 10,
        max_workers: int = 5,
    ):
        """Initialize the news crawler."""
        self.config_path = config_path
        self.db_path = db_path
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_workers = max_workers
        
        # Initialize components
        self.site_configs = SiteConfigLoader.load(config_path)
        self.database = Database(db_path)
        self.rss_parser = RSSParser(user_agent, timeout)
        self.web_scraper = WebScraper(user_agent, timeout)
        
        print(f"Initialized NewsCrawler with {len(self.site_configs)} sites")
    
    def crawl_all(self, use_rss: bool = True, use_scraping: bool = True) -> Dict[str, Any]:
        """Crawl all configured sites."""
        start_time = time.time()
        total_articles = 0
        
        if use_rss:
            rss_articles = self.crawl_rss_feeds()
            total_articles += len(rss_articles)
            print(f"Crawled {len(rss_articles)} articles from RSS feeds")
        
        if use_scraping:
            scraped_articles = self.crawl_websites()
            total_articles += len(scraped_articles)
            print(f"Crawled {len(scraped_articles)} articles from web scraping")
        
        elapsed = time.time() - start_time
        print(f"Crawling completed in {elapsed:.2f} seconds")
        
        return {
            'total_articles': total_articles,
            'rss_articles': len(rss_articles) if use_rss else 0,
            'scraped_articles': len(scraped_articles) if use_scraping else 0,
            'elapsed_time': elapsed,
        }
    
    def crawl_rss_feeds(self) -> List[Article]:
        """Crawl all RSS feeds."""
        articles = []
        
        # Filter sites with RSS feeds
        rss_sites = [s for s in self.site_configs if s.rss_feed and s.use_rss]
        
        for site_config in rss_sites:
            try:
                site_articles = self.rss_parser.parse_feed(site_config.rss_feed, site_config)
                # Save articles to database
                for article in site_articles:
                    saved_article = self.database.save_article(article)
                    articles.append(saved_article)
            except Exception as e:
                print(f"Error crawling RSS feed for {site_config.name}: {e}")
        
        return articles
    
    def crawl_websites(self) -> List[Article]:
        """Crawl websites directly."""
        articles = []
        
        # Filter sites that use scraping
        scrape_sites = [s for s in self.site_configs if s.use_scraping]
        
        for site_config in scrape_sites:
            try:
                site_articles = self.web_scraper.scrape_site(site_config)
                # Save articles to database
                for article in site_articles:
                    saved_article = self.database.save_article(article)
                    articles.append(saved_article)
            except Exception as e:
                print(f"Error crawling website {site_config.name}: {e}")
        
        return articles
    
    def crawl_and_enrich(self, use_rss: bool = True, use_scraping: bool = True) -> Dict[str, Any]:
        """Crawl articles and enrich them with full content."""
        result = self.crawl_all(use_rss, use_scraping)
        
        # Get all articles without content
        articles_to_enrich = self.database.get_all_articles(limit=100)
        
        enriched_count = 0
        for article in articles_to_enrich:
            if not article.content and article.url:
                # Try to enrich with full content
                for site_config in self.site_configs:
                    if site_config.name == article.source:
                        full_article = self.web_scraper.scrape_article_page(article.url, site_config)
                        if full_article and full_article.content:
                            article.content = full_article.content
                            article.summary = full_article.summary if full_article.summary else article.summary
                            article.published_at = full_article.published_at or article.published_at
                            article.author = full_article.author or article.author
                            article.image_url = full_article.image_url or article.image_url
                            self.database.update_article(article)
                            enriched_count += 1
                        break
        
        result['enriched_articles'] = enriched_count
        return result
    
    def get_recent_articles(self, hours: int = 24, limit: int = 50) -> List[Article]:
        """Get recently crawled articles."""
        return self.database.get_recent_articles(hours, limit)
    
    def get_articles_by_source(self, source: str, limit: int = 20) -> List[Article]:
        """Get articles from a specific source."""
        return self.database.get_articles_by_source(source, limit)
    
    def search_articles(self, query: str, limit: int = 10) -> List[Article]:
        """Search articles by query."""
        return self.database.search_articles(query, limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""
        return {
            **self.database.get_stats(),
            'configured_sites': len(self.site_configs),
            'rss_sites': len([s for s in self.site_configs if s.rss_feed]),
        }
    
    async def async_crawl_all(self, use_rss: bool = True, use_scraping: bool = True) -> Dict[str, Any]:
        """Async version of crawl_all for concurrent crawling."""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit RSS crawling tasks
            rss_futures = []
            if use_rss:
                rss_sites = [s for s in self.site_configs if s.rss_feed and s.use_rss]
                for site_config in rss_sites:
                    future = loop.run_in_executor(
                        executor,
                        self.rss_parser.parse_feed,
                        site_config.rss_feed,
                        site_config,
                    )
                    rss_futures.append(future)
            
            # Submit scraping tasks
            scrape_futures = []
            if use_scraping:
                scrape_sites = [s for s in self.site_configs if s.use_scraping]
                for site_config in scrape_sites:
                    future = loop.run_in_executor(
                        executor,
                        self.web_scraper.scrape_site,
                        site_config,
                    )
                    scrape_futures.append(future)
            
            # Wait for all tasks
            rss_results = await asyncio.gather(*rss_futures, return_exceptions=True)
            scrape_results = await asyncio.gather(*scrape_futures, return_exceptions=True)
        
        # Process results
        total_articles = 0
        for result in rss_results:
            if isinstance(result, list):
                for article in result:
                    self.database.save_article(article)
                    total_articles += 1
        
        for result in scrape_results:
            if isinstance(result, list):
                for article in result:
                    self.database.save_article(article)
                    total_articles += 1
        
        return {
            'total_articles': total_articles,
            'rss_articles': sum(len(r) for r in rss_results if isinstance(r, list)),
            'scraped_articles': sum(len(r) for r in scrape_results if isinstance(r, list)),
        }
