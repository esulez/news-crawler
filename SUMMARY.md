# News Crawler - Summary

## Overview

I've created a comprehensive news crawler system that aggregates articles from multiple websites, deduplicates similar articles, and displays them in a web dashboard. Here's what was built:

## System Architecture

```
news_crawler/
├── crawler/                    # Crawling modules
│   ├── __init__.py
│   ├── crawler.py              # Main crawler class
│   ├── rss_parser.py           # RSS feed parser
│   ├── web_scraper.py          # Web scraping module
│   └── site_config.py          # Site configuration loader
│
├── storage/                    # Storage modules
│   ├── __init__.py
│   └── database.py             # SQLite database with Article and Cluster models
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── deduplicator.py         # Deduplication and clustering logic
│   └── text_processor.py       # Text processing for similarity comparison
│
├── dashboard/                  # Web dashboard (Flask)
│   ├── __init__.py
│   ├── app.py                  # Flask application
│   ├── routes.py               # API routes
│   ├── templates/              # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── clusters.html
│   │   ├── article.html
│   │   └── sources.html
│   └── static/                 # Static files (CSS, JS)
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
│
├── config/                     # Configuration files
│   └── sites.yaml              # Website configurations
│
├── data/                       # Database and cached data
│
├── main.py                     # Entry point
├── run.sh                      # Run script
├── test_system.py              # System test script
├── README.md                   # Documentation
└── requirements.txt            # Dependencies
```

## Key Features

### 1. Multi-Source Crawling
- **RSS Feed Parser**: Fetches articles from RSS feeds
- **Web Scraper**: Scrapes articles directly from websites
- **Configurable**: Add any website with custom CSS selectors
- **Pre-configured Sites**: TechCrunch, The Verge, Ars Technica, Wired, BBC Technology, Hacker News

### 2. Article Deduplication & Clustering
- **TF-IDF Vectorization**: Converts article text to numerical vectors
- **Cosine Similarity**: Measures similarity between articles
- **Configurable Threshold**: Adjust similarity threshold (default: 0.4)
- **Cluster Management**: Groups similar articles into clusters
- **Representative Articles**: Each cluster has a representative article

### 3. Web Dashboard
- **Home Page**: Browse all articles with filtering and search
- **Sources Page**: View articles by source
- **Clusters Page**: Explore article clusters
- **Article Details**: View full article content and similar articles
- **Real-time Actions**: Trigger crawls and deduplication from the UI

### 4. REST API
- `/api/articles` - Get articles with filters
- `/api/clusters` - Get article clusters
- `/api/crawl` - Trigger crawling
- `/api/deduplicate` - Trigger deduplication
- `/api/stats` - Get system statistics

### 5. Storage
- **SQLite Database**: Lightweight, file-based storage
- **Article Model**: Stores title, URL, content, source, metadata
- **Cluster Model**: Groups similar articles
- **Indexes**: Optimized for fast queries

## Technologies Used

- **Python 3.7+**
- **Flask** - Web framework
- **BeautifulSoup** - HTML parsing
- **feedparser** - RSS feed parsing
- **scikit-learn** - Text processing and clustering
- **SQLite** - Database
- **Bootstrap** - Frontend styling
- **Font Awesome** - Icons

## How to Use

### Installation
```bash
cd news_crawler
pip install -r requirements.txt
mkdir -p data
```

### Run the Dashboard
```bash
python main.py --dashboard
# Dashboard will be available at http://localhost:5000
```

### Crawl Articles
```bash
python main.py --crawl
```

### Deduplicate Articles
```bash
python main.py --deduplicate
```

### Crawl and Enrich
```bash
python main.py --enrich
```

## Configuration

Edit `config/sites.yaml` to add or modify websites:

```yaml
sites:
  - name: "My News Site"
    url: "https://example.com"
    rss_feed: "https://example.com/feed/"
    category: "news"
    article_selector: "article"
    title_selector: "h2 a"
    summary_selector: "p.summary"
    date_selector: "time"
    link_selector: "h2 a"
```

## Testing

Run the system test:
```bash
python test_system.py
```

All tests should pass:
- Database functionality
- Text processing
- Deduplication
- Crawler configuration

## Customization

### Deduplication Settings
Adjust in `utils/deduplicator.py`:
- `similarity_threshold`: Minimum similarity to cluster articles (default: 0.4)
- `min_cluster_size`: Minimum number of articles to form a cluster (default: 2)

### Text Processing
Adjust in `utils/text_processor.py`:
- `min_df`: Minimum document frequency for TF-IDF (default: 1)
- `max_df`: Maximum document frequency for TF-IDF (default: 1.0)
- `ngram_range`: Range of n-grams to use (default: (1, 2))

## Dashboard Features

### Home Page
- View all articles in a card-based layout
- Filter by source, category, or time
- Search articles by keyword
- Toggle between "All Articles", "Recent (24h)", and "Deduplicated" views
- Load more articles with pagination

### Sources Page
- Browse articles by source
- See article counts per source
- View recent articles from each source

### Clusters Page
- View all article clusters
- See cluster topics and article counts
- Expand clusters to view all articles
- Delete individual clusters or reset all clusters

### Article Details Page
- View full article content
- See metadata (source, date, author, category)
- View similar articles
- Navigate to cluster or original URL

## Performance Considerations

1. **Crawling**: Use RSS feeds when available (faster than scraping)
2. **Deduplication**: Process in batches for large datasets
3. **Storage**: SQLite is suitable for small to medium datasets
4. **Similarity Calculation**: TF-IDF with n-grams provides good balance between accuracy and performance

## Future Enhancements

1. **Scheduled Crawling**: Add cron jobs or Celery for periodic crawling
2. **Email Notifications**: Send alerts for new articles
3. **Advanced Clustering**: Use embeddings (BERT, etc.) for better similarity
4. **User Authentication**: Add user accounts and preferences
5. **Export**: Add CSV/JSON export functionality
6. **More Sites**: Add additional news sources
7. **Custom Filters**: Allow users to define custom filters
8. **API Key Management**: Add support for sites requiring API keys

## Files Created

- `news_crawler/` - Main project directory
- All Python modules, templates, and configuration files
- `README.md` - Complete documentation
- `requirements.txt` - Dependencies
- `test_system.py` - System tests

## Summary

The News Crawler system is now fully functional with:
- ✅ Multi-site crawling (RSS and web scraping)
- ✅ Article storage with SQLite
- ✅ Deduplication and clustering
- ✅ Web dashboard with filtering and search
- ✅ REST API for programmatic access
- ✅ Configuration management
- ✅ System tests

The system is ready to use and can be extended with additional features as needed.
