#!/usr/bin/env python3
"""Test script to verify the complete news crawler system."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from storage.database import Database, Article
from crawler.crawler import NewsCrawler
from utils.deduplicator import Deduplicator
from datetime import datetime


def test_database():
    """Test database functionality."""
    print("Testing database...")
    db_path = 'data/test_system.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    
    # Test save and retrieve
    article = Article(
        title='Test Article',
        url='https://example.com/test',
        summary='Test summary',
        content='Test content',
        source='Test Source',
        category='tech',
        published_at=datetime.now(),
    )
    
    saved = db.save_article(article)
    assert saved.id is not None
    
    retrieved = db.get_article_by_url('https://example.com/test')
    assert retrieved is not None
    assert retrieved.title == 'Test Article'
    
    # Test stats
    stats = db.get_stats()
    assert stats['total_articles'] == 1
    
    os.remove(db_path)
    print("  ✓ Database test passed")


def test_text_processor():
    """Test text processing."""
    print("Testing text processor...")
    from utils.text_processor import TextProcessor
    
    processor = TextProcessor()
    
    # Test preprocessing
    text = 'This is a test. Python is great!'
    processed = processor.preprocess_text(text)
    assert 'Python' in processed
    assert 'test' in processed
    
    # Test similarity
    text1 = 'Python is a great language'
    text2 = 'Python is an excellent language'
    similarity = processor.calculate_similarity(text1, text2)
    assert 0 < similarity <= 1
    
    # Test keywords
    keywords = processor.extract_keywords(text, top_n=2)
    assert len(keywords) <= 2
    
    print("  ✓ Text processor test passed")


def test_deduplicator():
    """Test deduplication."""
    print("Testing deduplicator...")
    db_path = 'data/test_dedup_system.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    
    # Create similar articles with more text
    articles = [
        Article(
            title='Python 3.10 Released with New Features',
            url='https://example.com/python1',
            summary='Python 3.10 has been released',
            content='Python 3.10 has been released with many new features and improvements. This is a major update for developers.',
            source='Source A',
        ),
        Article(
            title='Python 3.10 is Now Available',
            url='https://example.com/python2',
            summary='Python 3.10 is now available',
            content='Python 3.10 is now available for download with exciting new features. This is a major release for the Python community.',
            source='Source B',
        ),
        Article(
            title='JavaScript News',
            url='https://example.com/js',
            summary='JavaScript updates',
            content='JavaScript has new updates coming soon.',
            source='Source C',
        ),
    ]
    
    for article in articles:
        db.save_article(article)
    
    # Run deduplication
    dedup = Deduplicator(db_path, similarity_threshold=0.35, min_cluster_size=2)
    result = dedup.deduplicate()
    
    assert result['clusters_created'] >= 1
    
    # Check clusters
    clusters = db.get_all_clusters()
    assert len(clusters) >= 1
    
    # Check that similar articles are clustered
    clustered_articles = [a for a in db.get_all_articles() if a.cluster_id is not None]
    assert len(clustered_articles) >= 2
    
    os.remove(db_path)
    print("  ✓ Deduplicator test passed")


def test_crawler_config():
    """Test crawler configuration loading."""
    print("Testing crawler configuration...")
    from crawler.site_config import SiteConfigLoader
    
    # Test loading default config
    configs = SiteConfigLoader.create_default_configs()
    assert len(configs) > 0
    
    # Check that TechCrunch is in the defaults
    site_names = [c.name for c in configs]
    assert 'TechCrunch' in site_names
    
    print("  ✓ Crawler configuration test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("News Crawler System Test")
    print("=" * 60)
    
    try:
        test_database()
        test_text_processor()
        test_deduplicator()
        test_crawler_config()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
