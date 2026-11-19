"""Web scraper for extracting articles from HTML pages."""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
from storage.database import Article
from crawler.site_config import SiteConfig
import re


class WebScraper:
    """Scrape articles from HTML pages."""
    
    def __init__(self, user_agent: str = "NewsCrawler/1.0", timeout: int = 10):
        """Initialize the web scraper."""
        self.user_agent = user_agent
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def scrape_site(self, site_config: SiteConfig, max_articles: int = 20) -> List[Article]:
        """Scrape articles from a website's homepage."""
        try:
            response = self.session.get(site_config.url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article elements
            article_elements = soup.select(site_config.article_selector)
            if not article_elements:
                # Try fallback selectors
                for fallback in ['article', '.article', '.post', '.story', 'div.post']:
                    article_elements = soup.select(fallback)
                    if article_elements:
                        break
            
            articles = []
            for element in article_elements[:max_articles]:
                article = self._element_to_article(element, site_config)
                if article:
                    articles.append(article)
            
            return articles
        except Exception as e:
            print(f"Error scraping {site_config.url}: {e}")
            return []
    
    def scrape_article_page(self, url: str, site_config: SiteConfig) -> Optional[Article]:
        """Scrape a single article page."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_text(soup, site_config.title_selector)
            if not title:
                title = soup.title.string if soup.title else ''
            
            # Extract content
            content = self._extract_text(soup, site_config.content_selector)
            
            # Extract summary
            summary = self._extract_text(soup, site_config.summary_selector)
            if not summary:
                # Use first paragraph if available
                first_p = soup.find('p')
                summary = first_p.get_text().strip() if first_p else content[:200]
            
            # Extract date
            date_str = self._extract_text(soup, site_config.date_selector)
            published_at = None
            if date_str:
                try:
                    published_at = date_parser.parse(date_str)
                except:
                    pass
            
            # Extract author
            author = self._extract_text(soup, site_config.author_selector)
            
            # Extract image
            image_url = ''
            img_element = soup.select_one(site_config.image_selector)
            if img_element and img_element.name == 'img':
                image_url = img_element.get('src', '')
                if image_url and not image_url.startswith('http'):
                    # Make relative URL absolute
                    from urllib.parse import urljoin
                    image_url = urljoin(url, image_url)
            
            article = Article(
                title=title.strip(),
                url=url,
                summary=summary.strip(),
                content=content.strip(),
                source=site_config.name,
                category=site_config.category,
                published_at=published_at,
                author=author.strip() if author else '',
                image_url=image_url,
            )
            
            return article
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None
    
    def _element_to_article(self, element: Any, site_config: SiteConfig) -> Optional[Article]:
        """Convert an HTML element to an Article object."""
        try:
            # Extract title
            title_element = element.select_one(site_config.title_selector)
            title = title_element.get_text().strip() if title_element else ''
            if not title:
                return None
            
            # Extract URL
            link_element = element.select_one(site_config.link_selector)
            url = link_element.get('href') if link_element else ''
            if not url:
                # Try to find any link
                link_element = element.find('a')
                url = link_element.get('href') if link_element else ''
            
            if not url:
                return None
            
            # Make relative URL absolute
            from urllib.parse import urljoin
            if url and not url.startswith('http'):
                url = urljoin(site_config.url, url)
            
            # Extract summary
            summary_element = element.select_one(site_config.summary_selector)
            summary = summary_element.get_text().strip() if summary_element else ''
            
            # Extract date
            date_element = element.select_one(site_config.date_selector)
            date_str = date_element.get_text().strip() if date_element else ''
            published_at = None
            if date_str:
                try:
                    published_at = date_parser.parse(date_str)
                except:
                    pass
            
            # Extract author
            author_element = element.select_one(site_config.author_selector)
            author = author_element.get_text().strip() if author_element else ''
            
            article = Article(
                title=title,
                url=url,
                summary=summary,
                content='',  # Will be fetched later if needed
                source=site_config.name,
                category=site_config.category,
                published_at=published_at,
                author=author,
            )
            
            return article
        except Exception as e:
            print(f"Error converting element to article: {e}")
            return None
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extract text from an element using a selector."""
        if not selector:
            return ''
        
        element = soup.select_one(selector)
        if element:
            return element.get_text().strip()
        return ''
    
    def scrape_article_urls(self, site_config: SiteConfig, max_articles: int = 20) -> List[str]:
        """Scrape article URLs from a website."""
        try:
            response = self.session.get(site_config.url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links that look like articles
            urls = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if self._is_article_url(href, site_config.url):
                    # Make absolute URL
                    from urllib.parse import urljoin
                    full_url = urljoin(site_config.url, href)
                    if full_url not in urls:
                        urls.append(full_url)
                    if len(urls) >= max_articles:
                        break
            
            return urls
        except Exception as e:
            print(f"Error scraping URLs from {site_config.url}: {e}")
            return []
    
    def _is_article_url(self, url: str, base_url: str) -> bool:
        """Check if a URL looks like an article URL."""
        # Skip non-HTTP URLs
        if not url or url.startswith('javascript:') or url.startswith('mailto:'):
            return False
        
        # Skip anchor links
        if url.startswith('#'):
            return False
        
        # Check for common article URL patterns
        article_patterns = [
            '/article/', '/articles/', '/news/', '/post/', '/story/',
            '/2024/', '/2023/', '/2025/',  # Date-based URLs
            '.html', '.htm',
        ]
        
        url_lower = url.lower()
        for pattern in article_patterns:
            if pattern in url_lower:
                return True
        
        # If URL is relative and contains slashes, it's likely an article
        if url.startswith('/') and '/' in url[1:]:
            return True
        
        return False
