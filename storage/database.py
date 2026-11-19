"""Database module for storing and retrieving articles."""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import hashlib


@dataclass
class Article:
    """Represents a news article."""
    id: Optional[int] = None
    title: str = ""
    url: str = ""
    summary: str = ""
    content: str = ""
    source: str = ""
    category: str = ""
    published_at: Optional[datetime] = None
    crawled_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    image_url: str = ""
    
    # For deduplication
    content_hash: str = ""
    cluster_id: Optional[int] = None
    is_representative: bool = False
    
    def __post_init__(self):
        if not self.content_hash and self.content:
            self.content_hash = self._generate_hash(self.content)
    
    @staticmethod
    def _generate_hash(text: str) -> str:
        """Generate a hash for the content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:64]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'content': self.content,
            'source': self.source,
            'category': self.category,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'crawled_at': self.crawled_at.isoformat(),
            'author': self.author,
            'image_url': self.image_url,
            'content_hash': self.content_hash,
            'cluster_id': self.cluster_id,
            'is_representative': self.is_representative,
        }


@dataclass
class ArticleCluster:
    """Represents a cluster of similar articles."""
    id: Optional[int] = None
    topic: str = ""
    representative_article_id: Optional[int] = None
    article_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cluster to dictionary."""
        return {
            'id': self.id,
            'topic': self.topic,
            'representative_article_id': self.representative_article_id,
            'article_count': self.article_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Database:
    """SQLite database for storing articles and clusters."""
    
    def __init__(self, db_path: str = "data/news.db"):
        """Initialize the database."""
        self.db_path = db_path
        self._ensure_directory()
        self._init_db()
    
    def _ensure_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Articles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    summary TEXT,
                    content TEXT,
                    source TEXT NOT NULL,
                    category TEXT DEFAULT 'tech',
                    published_at TEXT,
                    crawled_at TEXT NOT NULL,
                    author TEXT,
                    image_url TEXT,
                    content_hash TEXT,
                    cluster_id INTEGER,
                    is_representative BOOLEAN DEFAULT 0,
                    FOREIGN KEY (cluster_id) REFERENCES clusters(id)
                )
            """)
            
            # Clusters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    representative_article_id INTEGER,
                    article_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (representative_article_id) REFERENCES articles(id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON articles(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON articles(content_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cluster ON articles(cluster_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON articles(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_published ON articles(published_at)")
            
            conn.commit()
    
    def save_article(self, article: Article) -> Article:
        """Save an article to the database."""
        # Check if article already exists by URL
        existing = self.get_article_by_url(article.url)
        if existing:
            return existing
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO articles (
                    title, url, summary, content, source, category, 
                    published_at, crawled_at, author, image_url, content_hash, cluster_id, is_representative
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.title,
                article.url,
                article.summary,
                article.content,
                article.source,
                article.category,
                article.published_at.isoformat() if article.published_at else None,
                article.crawled_at.isoformat(),
                article.author,
                article.image_url,
                article.content_hash,
                article.cluster_id,
                article.is_representative,
            ))
            article.id = cursor.lastrowid
            conn.commit()
        
        return article
    
    def get_article_by_url(self, url: str) -> Optional[Article]:
        """Get an article by its URL."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE url = ?", (url,))
            row = cursor.fetchone()
            if row:
                return self._row_to_article(row)
        return None
    
    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """Get an article by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_article(row)
        return None
    
    def _row_to_article(self, row: tuple) -> Article:
        """Convert a database row to an Article object."""
        return Article(
            id=row[0],
            title=row[1],
            url=row[2],
            summary=row[3],
            content=row[4],
            source=row[5],
            category=row[6],
            published_at=datetime.fromisoformat(row[7]) if row[7] else None,
            crawled_at=datetime.fromisoformat(row[8]),
            author=row[9],
            image_url=row[10],
            content_hash=row[11],
            cluster_id=row[12],
            is_representative=bool(row[13]),
        )
    
    def get_all_articles(self, limit: int = None, offset: int = 0) -> List[Article]:
        """Get all articles with optional pagination."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM articles ORDER BY crawled_at DESC"
            params = []
            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params = [limit, offset]
            cursor.execute(query, params)
            return [self._row_to_article(row) for row in cursor.fetchall()]
    
    def get_articles_by_source(self, source: str, limit: int = None) -> List[Article]:
        """Get articles from a specific source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM articles WHERE source = ? ORDER BY crawled_at DESC"
            params = [source]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            cursor.execute(query, params)
            return [self._row_to_article(row) for row in cursor.fetchall()]
    
    def get_recent_articles(self, hours: int = 24, limit: int = None) -> List[Article]:
        """Get articles crawled within the last N hours."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM articles 
                WHERE crawled_at >= datetime('now', ?) 
                ORDER BY crawled_at DESC
            """
            params = [f"-{hours} hours"]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            cursor.execute(query, params)
            return [self._row_to_article(row) for row in cursor.fetchall()]
    
    def get_articles_without_cluster(self) -> List[Article]:
        """Get articles that are not assigned to any cluster."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE cluster_id IS NULL")
            return [self._row_to_article(row) for row in cursor.fetchall()]
    
    def get_articles_by_cluster(self, cluster_id: int) -> List[Article]:
        """Get all articles in a cluster."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE cluster_id = ?", (cluster_id,))
            return [self._row_to_article(row) for row in cursor.fetchall()]
    
    def get_cluster_by_id(self, cluster_id: int) -> Optional[ArticleCluster]:
        """Get a cluster by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clusters WHERE id = ?", (cluster_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_cluster(row)
        return None
    
    def _row_to_cluster(self, row: tuple) -> ArticleCluster:
        """Convert a database row to an ArticleCluster object."""
        return ArticleCluster(
            id=row[0],
            topic=row[1],
            representative_article_id=row[2],
            article_count=row[3],
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5]),
        )
    
    def get_all_clusters(self) -> List[ArticleCluster]:
        """Get all clusters."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clusters ORDER BY updated_at DESC")
            return [self._row_to_cluster(row) for row in cursor.fetchall()]
    
    def save_cluster(self, cluster: ArticleCluster) -> ArticleCluster:
        """Save a cluster to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if cluster.id:
                # Update existing cluster
                cursor.execute("""
                    UPDATE clusters SET 
                        topic = ?, representative_article_id = ?, 
                        article_count = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    cluster.topic,
                    cluster.representative_article_id,
                    cluster.article_count,
                    cluster.updated_at.isoformat(),
                    cluster.id,
                ))
            else:
                # Insert new cluster
                cursor.execute("""
                    INSERT INTO clusters (
                        topic, representative_article_id, article_count, 
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    cluster.topic,
                    cluster.representative_article_id,
                    cluster.article_count,
                    cluster.created_at.isoformat(),
                    cluster.updated_at.isoformat(),
                ))
                cluster.id = cursor.lastrowid
            conn.commit()
        return cluster
    
    def assign_article_to_cluster(self, article_id: int, cluster_id: int) -> bool:
        """Assign an article to a cluster."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE articles SET cluster_id = ? WHERE id = ?",
                (cluster_id, article_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def set_representative_article(self, article_id: int, is_representative: bool = True) -> bool:
        """Set an article as representative of its cluster."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE articles SET is_representative = ? WHERE id = ?",
                (int(is_representative), article_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def update_article(self, article: Article) -> bool:
        """Update an existing article."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE articles SET 
                    title = ?, summary = ?, content = ?, category = ?, 
                    published_at = ?, author = ?, image_url = ?, 
                    content_hash = ?, cluster_id = ?, is_representative = ?
                WHERE id = ?
            """, (
                article.title,
                article.summary,
                article.content,
                article.category,
                article.published_at.isoformat() if article.published_at else None,
                article.author,
                article.image_url,
                article.content_hash,
                article.cluster_id,
                article.is_representative,
                article.id,
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_article(self, article_id: int) -> bool:
        """Delete an article from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_cluster(self, cluster_id: int) -> bool:
        """Delete a cluster and unassign its articles."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # First, unassign articles from the cluster
            cursor.execute(
                "UPDATE articles SET cluster_id = NULL WHERE cluster_id = ?",
                (cluster_id,)
            )
            # Then delete the cluster
            cursor.execute("DELETE FROM clusters WHERE id = ?", (cluster_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM articles")
            total_articles = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM clusters")
            total_clusters = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT source) FROM articles")
            total_sources = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM articles WHERE cluster_id IS NOT NULL")
            clustered_articles = cursor.fetchone()[0]
            
            return {
                'total_articles': total_articles,
                'total_clusters': total_clusters,
                'total_sources': total_sources,
                'clustered_articles': clustered_articles,
                'unclustered_articles': total_articles - clustered_articles,
            }
    
    def search_articles(self, query: str, limit: int = 10) -> List[Article]:
        """Search articles by title or content."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM articles 
                WHERE title LIKE ? OR summary LIKE ? OR content LIKE ?
                ORDER BY crawled_at DESC
                LIMIT ?
            """, (search_pattern, search_pattern, search_pattern, limit))
            return [self._row_to_article(row) for row in cursor.fetchall()]
