# Quick Start Guide

## Get Started in 5 Minutes

### 1. Install Dependencies

```bash
cd news_crawler
pip install -r requirements.txt
```

### 2. Create Data Directory

```bash
mkdir -p data
```

### 3. Run the Dashboard

```bash
python main.py --dashboard
```

Your dashboard will be available at: **http://localhost:5000**

### 4. Crawl Your First Articles

Open your browser and go to http://localhost:5000

Click the "Crawl" button in the top navigation bar to fetch articles from configured sites.

### 5. Deduplicate Articles

Click the "Deduplicate" button to cluster similar articles together.

## Command Line Usage

### Crawl Articles

```bash
# Crawl all sites
python main.py --crawl

# Crawl and enrich with full content
python main.py --enrich

# Crawl with custom config
python main.py --crawl --config config/my_sites.yaml
```

### Deduplicate Articles

```bash
# Run deduplication
python main.py --deduplicate

# Run with custom database path
python main.py --deduplicate --db-path data/my_news.db
```

### Run Dashboard

```bash
# Default (localhost:5000)
python main.py --dashboard

# Custom host and port
python main.py --dashboard --host 0.0.0.0 --port 8080

# Production mode (debug off)
python main.py --dashboard --debug false
```

## Configuration

### Add a New Website

Edit `config/sites.yaml`:

```yaml
sites:
  - name: "My Favorite News"
    url: "https://mynews.com"
    rss_feed: "https://mynews.com/feed/"
    category: "news"
```

### Custom Selectors

For websites without RSS feeds, add scraping selectors:

```yaml
sites:
  - name: "Custom Site"
    url: "https://custom.com"
    rss_feed: null
    use_rss: false
    use_scraping: true
    article_selector: "div.article"
    title_selector: "h2.title a"
    summary_selector: "p.summary"
    date_selector: "span.date"
    link_selector: "h2.title a"
    category: "tech"
```

## Dashboard Features

### Navigation

- **Home**: View all articles
- **Sources**: Browse by source
- **Clusters**: View deduplicated article groups

### Actions

- **Crawl**: Fetch new articles from all configured sites
- **Deduplicate**: Cluster similar articles
- **Search**: Find articles by keyword
- **Filter**: Filter by source, category, or time

### Article Actions

- Click article title to view details
- Click "Read More" to visit original article
- Click "View Cluster" to see similar articles

## Troubleshooting

### Database Issues

If you get database errors, try:

```bash
rm data/news.db
python main.py --dashboard
```

### Import Errors

Make sure you're running from the `news_crawler` directory:

```bash
cd /path/to/news_crawler
python main.py --dashboard
```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

## Next Steps

1. **Add more sites**: Edit `config/sites.yaml`
2. **Customize deduplication**: Adjust `similarity_threshold` in `utils/deduplicator.py`
3. **Deploy**: Use gunicorn or uWSGI for production
4. **Schedule**: Set up cron jobs for regular crawling

## Example: Full Workflow

```bash
# 1. Install
pip install -r requirements.txt

# 2. Create data directory
mkdir -p data

# 3. Crawl articles
python main.py --crawl

# 4. Deduplicate
python main.py --deduplicate

# 5. Start dashboard
python main.py --dashboard

# 6. Open browser
# Navigate to http://localhost:5000
```

## Tips

- **Use RSS feeds**: They're faster and more reliable than scraping
- **Start with few sites**: Add more gradually to avoid rate limiting
- **Adjust similarity threshold**: Lower values create more clusters, higher values create fewer
- **Check logs**: The console will show crawling progress and errors

## Need Help?

- Check `README.md` for detailed documentation
- Run `python test_system.py` to verify everything works
- See `SUMMARY.md` for system architecture overview
