#!/usr/bin/env python3
"""Main entry point for the News Crawler application."""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from crawler.crawler import NewsCrawler
from utils.deduplicator import Deduplicator
from storage.database import Database
from dashboard.app import create_app


def main():
    """Main function to run the news crawler."""
    parser = argparse.ArgumentParser(
        description="News Crawler - Aggregate and deduplicate news articles"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/sites.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='data/news.db',
        help='Path to SQLite database'
    )
    parser.add_argument(
        '--crawl',
        action='store_true',
        help='Run crawler only'
    )
    parser.add_argument(
        '--deduplicate',
        action='store_true',
        help='Run deduplication only'
    )
    parser.add_argument(
        '--enrich',
        action='store_true',
        help='Crawl and enrich articles with full content'
    )
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Run dashboard only'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host for dashboard server'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port for dashboard server'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode for dashboard'
    )
    
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    # Check if we should run dashboard
    if args.dashboard or not (args.crawl or args.deduplicate or args.enrich):
        # Run dashboard by default if no specific action
        print("Starting News Crawler Dashboard...")
        print(f"Dashboard will be available at http://{args.host}:{args.port}")
        
        app = create_app(args.config, args.db_path)
        app.run(host=args.host, port=args.port, debug=args.debug)
    else:
        # Run crawler operations
        crawler = NewsCrawler(args.config, args.db_path)
        deduplicator = Deduplicator(args.db_path)
        
        if args.crawl:
            print("Starting crawl...")
            result = crawler.crawl_all()
            print(f"Crawl complete: {result['total_articles']} articles found")
        
        if args.enrich:
            print("Starting crawl with enrichment...")
            result = crawler.crawl_and_enrich()
            print(f"Crawl and enrich complete: {result['total_articles']} articles, {result['enriched_articles']} enriched")
        
        if args.deduplicate:
            print("Running deduplication...")
            result = deduplicator.deduplicate()
            print(f"Deduplication complete: {result['clusters_created']} clusters created, {result['articles_clustered']} articles clustered")
        
        # Print stats
        stats = crawler.get_stats()
        print("\nStatistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
