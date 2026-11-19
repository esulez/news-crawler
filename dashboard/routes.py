"""Routes for the news dashboard."""

from flask import Blueprint, render_template, jsonify, request, current_app
from datetime import datetime, timedelta
import json


main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@main_routes.route('/api/articles')
def get_articles():
    """Get articles with optional filters."""
    db = current_app.database
    
    # Get query parameters
    source = request.args.get('source')
    category = request.args.get('category')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    hours = request.args.get('hours', 24, type=int)
    cluster = request.args.get('cluster', type=int)
    search = request.args.get('search')
    deduplicated = request.args.get('deduplicated', 'false').lower() == 'true'
    
    # Get articles
    if search:
        articles = db.search_articles(search, limit)
    elif cluster:
        articles = db.get_articles_by_cluster(cluster)
    elif deduplicated:
        # Get representative articles only
        deduplicator = current_app.deduplicator
        articles = deduplicator.get_representative_articles(limit)
    elif source:
        articles = db.get_articles_by_source(source, limit)
    elif hours > 0:
        articles = db.get_recent_articles(hours, limit)
    else:
        articles = db.get_all_articles(limit, offset)
    
    # Filter by category if specified
    if category:
        articles = [a for a in articles if a.category.lower() == category.lower()]
    
    # Convert to JSON
    articles_json = [a.to_dict() for a in articles]
    
    return jsonify({
        'articles': articles_json,
        'count': len(articles_json),
    })


@main_routes.route('/api/articles/<int:article_id>')
def get_article(article_id):
    """Get a single article by ID."""
    db = current_app.database
    article = db.get_article_by_id(article_id)
    
    if article:
        return jsonify(article.to_dict())
    else:
        return jsonify({'error': 'Article not found'}), 404


@main_routes.route('/api/clusters')
def get_clusters():
    """Get all clusters."""
    db = current_app.database
    clusters = db.get_all_clusters()
    
    clusters_json = [c.to_dict() for c in clusters]
    
    return jsonify({
        'clusters': clusters_json,
        'count': len(clusters_json),
    })


@main_routes.route('/api/clusters/<int:cluster_id>')
def get_cluster(cluster_id):
    """Get a cluster and its articles."""
    db = current_app.database
    deduplicator = current_app.deduplicator
    
    cluster = db.get_cluster_by_id(cluster_id)
    if not cluster:
        return jsonify({'error': 'Cluster not found'}), 404
    
    articles = deduplicator.get_cluster_articles(cluster_id)
    
    return jsonify({
        'cluster': cluster.to_dict(),
        'articles': [a.to_dict() for a in articles],
    })


@main_routes.route('/api/sources')
def get_sources():
    """Get all available sources."""
    db = current_app.database
    articles = db.get_all_articles(limit=1000)
    
    sources = set(a.source for a in articles)
    
    return jsonify({
        'sources': sorted(list(sources)),
    })


@main_routes.route('/api/categories')
def get_categories():
    """Get all available categories."""
    db = current_app.database
    articles = db.get_all_articles(limit=1000)
    
    categories = set(a.category for a in articles if a.category)
    
    return jsonify({
        'categories': sorted(list(categories)),
    })


@main_routes.route('/api/stats')
def get_stats():
    """Get dashboard statistics."""
    db = current_app.database
    crawler = current_app.crawler
    
    stats = db.get_stats()
    
    return jsonify({
        **stats,
        'last_updated': datetime.now().isoformat(),
    })


@main_routes.route('/api/crawl', methods=['POST'])
def crawl():
    """Trigger a crawl."""
    crawler = current_app.crawler
    
    use_rss = request.json.get('use_rss', True)
    use_scraping = request.json.get('use_scraping', True)
    
    result = crawler.crawl_all(use_rss=use_rss, use_scraping=use_scraping)
    
    return jsonify({
        'status': 'success',
        'result': result,
    })


@main_routes.route('/api/crawl-and-enrich', methods=['POST'])
def crawl_and_enrich():
    """Trigger a crawl with enrichment."""
    crawler = current_app.crawler
    
    use_rss = request.json.get('use_rss', True)
    use_scraping = request.json.get('use_scraping', True)
    
    result = crawler.crawl_and_enrich(use_rss=use_rss, use_scraping=use_scraping)
    
    return jsonify({
        'status': 'success',
        'result': result,
    })


@main_routes.route('/api/deduplicate', methods=['POST'])
def deduplicate():
    """Trigger deduplication."""
    deduplicator = current_app.deduplicator
    
    method = request.json.get('method', 'similarity')
    batch_size = request.json.get('batch_size', 100)
    
    if method == 'dbscan':
        result = deduplicator.cluster_all(method='dbscan', batch_size=batch_size)
    elif method == 'agglomerative':
        result = deduplicator.cluster_all(method='agglomerative', batch_size=batch_size)
    else:
        result = deduplicator.deduplicate(batch_size=batch_size)
    
    return jsonify({
        'status': 'success',
        'result': result,
    })


@main_routes.route('/api/reset-clusters', methods=['POST'])
def reset_clusters():
    """Reset all cluster assignments."""
    deduplicator = current_app.deduplicator
    
    count = deduplicator.reset_clusters()
    
    return jsonify({
        'status': 'success',
        'reset_count': count,
    })


@main_routes.route('/api/similar/<int:article_id>')
def get_similar(article_id):
    """Get articles similar to a given article."""
    deduplicator = current_app.deduplicator
    threshold = request.args.get('threshold', 0.8, type=float)
    
    similar_articles = deduplicator.find_similar_articles(article_id, threshold)
    
    return jsonify({
        'article_id': article_id,
        'similar_articles': [a.to_dict() for a in similar_articles],
        'count': len(similar_articles),
    })


@main_routes.route('/sources')
def sources_page():
    """Sources page."""
    return render_template('sources.html')


@main_routes.route('/clusters')
def clusters_page():
    """Clusters page."""
    return render_template('clusters.html')


@main_routes.route('/article/<int:article_id>')
def article_page(article_id):
    """Article detail page."""
    return render_template('article.html', article_id=article_id)
