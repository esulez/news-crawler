# News Crawler

A web crawler that aggregates news articles from multiple sources, deduplicates similar articles, and displays them in a dashboard.

## Features

- **Multi-source crawling**: Fetch articles from RSS feeds and direct web scraping
- **Deduplication**: Automatically cluster similar articles using text similarity
- **Dashboard**: Web interface to view, search, and manage articles
- **Storage**: SQLite database for persistent storage
- **Configuration**: YAML-based configuration for easy customization

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

```bash
# Clone or download the repository
cd news_crawler

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data
```

## Configuration

Edit `config/sites.yaml` to configure the websites to crawl:

```yaml
sites:
  - name: "TechCrunch"
    url: "https://techcrunch.com"
    rss_feed: "https://techcrunch.com/feed/"
    category: "tech"
  - name: "BBC Technology"
    url: "https://www.bbc.com/news/technology"
    rss_feed: "http://feeds.bbci.co.uk/news/technology/rss.xml"
    category: "tech"
```

## Usage

### Run the Dashboard

```bash
# Start the dashboard (default: http://localhost:5000)
python main.py --dashboard

# With custom host and port
python main.py --dashboard --host 0.0.0.0 --port 8080
```

### Crawl Articles

```bash
# Crawl all configured sites
python main.py --crawl

# Crawl and enrich with full content
python main.py --enrich
```

### Deduplicate Articles

```bash
# Run deduplication on unclustered articles
python main.py --deduplicate

# Run full clustering
python main.py --deduplicate
```

### Combined Operations

```bash
# Crawl, enrich, and deduplicate
python main.py --enrich --deduplicate
```

## Dashboard Features

- **Home**: View all articles with filtering and search
- **Sources**: Browse articles by source
- **Clusters**: View article clusters (similar articles grouped together)
- **Crawl**: Trigger new crawls from the UI
- **Deduplicate**: Run deduplication from the UI

## API Endpoints

- `GET /api/articles` - Get articles with optional filters
- `GET /api/articles/<id>` - Get a specific article
- `GET /api/clusters` - Get all clusters
- `GET /api/clusters/<id>` - Get a cluster and its articles
- `GET /api/sources` - Get all sources
- `GET /api/categories` - Get all categories
- `GET /api/stats` - Get statistics
- `POST /api/crawl` - Trigger a crawl
- `POST /api/deduplicate` - Trigger deduplication
- `POST /api/reset-clusters` - Reset all clusters

## Architecture

```
news_crawler/
├── crawler/           # Crawling modules
│   ├── crawler.py     # Main crawler class
│   ├── rss_parser.py  # RSS feed parser
│   ├── web_scraper.py # Web scraping module
│   └── site_config.py # Site configuration
├── storage/           # Storage modules
│   └── database.py    # SQLite database
├── utils/             # Utility modules
│   ├── deduplicator.py # Deduplication and clustering
│   └── text_processor.py # Text processing
├── dashboard/         # Web dashboard
│   ├── app.py         # Flask application
│   ├── routes.py      # API routes
│   └── templates/     # HTML templates
├── config/            # Configuration files
│   └── sites.yaml     # Site configurations
├── data/              # Database and cached data
└── main.py            # Entry point
```

## Customization

### Adding New Sites

Add a new site to `config/sites.yaml`:

```yaml
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

### Custom Selectors

Each site can have custom CSS selectors for:
- `article_selector`: Selector for article elements
- `title_selector`: Selector for article title
- `summary_selector`: Selector for article summary
- `content_selector`: Selector for full article content
- `date_selector`: Selector for publication date
- `link_selector`: Selector for article URL
- `author_selector`: Selector for author name
- `image_selector`: Selector for featured image

## Deduplication

The deduplication system uses TF-IDF vectorization and cosine similarity to identify similar articles. You can adjust the similarity threshold in the configuration:

```yaml
deduplication:
  similarity_threshold: 0.85  # Articles with similarity >= 85% are clustered
  use_tfidf: true
  min_cluster_size: 2  # Minimum number of articles to form a cluster
```

## Database

The application uses SQLite for storage. The database file is created automatically at `data/news.db`.

To reset the database, simply delete the file:

```bash
rm data/news.db
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License

## Acknowledgments

- Flask for the web framework
- BeautifulSoup for HTML parsing
- feedparser for RSS parsing
- scikit-learn for text processing and clustering
