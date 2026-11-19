"""Deduplication and clustering module for news articles."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from storage.database import Database, Article, ArticleCluster
from utils.text_processor import TextProcessor
from sklearn.cluster import DBSCAN, AgglomerativeClustering
import time


class Deduplicator:
    """Deduplicate and cluster similar articles."""
    
    def __init__(
        self,
        db_path: str = "data/news.db",
        similarity_threshold: float = 0.4,
        min_cluster_size: int = 2,
    ):
        """Initialize the deduplicator."""
        self.database = Database(db_path)
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.text_processor = TextProcessor(min_df=1, max_df=1.0, ngram_range=(1, 2))
    
    def deduplicate(self, batch_size: int = 100) -> Dict[str, Any]:
        """Run deduplication on unclustered articles."""
        start_time = time.time()
        
        # Get unclustered articles
        unclustered_articles = self.database.get_articles_without_cluster()
        
        if not unclustered_articles:
            return {
                'clusters_created': 0,
                'articles_clustered': 0,
                'elapsed_time': 0,
            }
        
        print(f"Deduplicating {len(unclustered_articles)} unclustered articles...")
        
        # Process in batches
        clusters_created = 0
        articles_clustered = 0
        
        for i in range(0, len(unclustered_articles), batch_size):
            batch = unclustered_articles[i:i + batch_size]
            batch_result = self._deduplicate_batch(batch)
            clusters_created += batch_result['clusters_created']
            articles_clustered += batch_result['articles_clustered']
        
        elapsed = time.time() - start_time
        
        return {
            'clusters_created': clusters_created,
            'articles_clustered': articles_clustered,
            'elapsed_time': elapsed,
        }
    
    def _deduplicate_batch(self, articles: List[Article]) -> Dict[str, Any]:
        """Deduplicate a batch of articles."""
        if not articles:
            return {'clusters_created': 0, 'articles_clustered': 0}
        
        # Extract texts for comparison
        texts = [a.title + ' ' + a.summary + ' ' + a.content for a in articles]
        
        # Calculate similarity matrix
        similarity_matrix = self.text_processor.calculate_batch_similarity(texts)
        
        # Find clusters using similarity threshold
        n = len(articles)
        clusters = []
        visited = set()
        
        for i in range(n):
            if i in visited:
                continue
            
            # Find all articles similar to article i
            cluster_indices = [i]
            for j in range(i + 1, n):
                if j not in visited and similarity_matrix[i][j] >= self.similarity_threshold:
                    cluster_indices.append(j)
                    visited.add(j)
            
            if len(cluster_indices) >= self.min_cluster_size:
                clusters.append(cluster_indices)
                for idx in cluster_indices:
                    visited.add(idx)
        
        # Create clusters in database
        clusters_created = 0
        articles_clustered = 0
        
        for cluster_indices in clusters:
            if len(cluster_indices) < self.min_cluster_size:
                continue
            
            # Create cluster
            cluster_articles = [articles[i] for i in cluster_indices]
            cluster = self._create_cluster(cluster_articles)
            
            if cluster:
                clusters_created += 1
                articles_clustered += len(cluster_articles)
        
        return {
            'clusters_created': clusters_created,
            'articles_clustered': articles_clustered,
        }
    
    def _create_cluster(self, articles: List[Article]) -> Optional[ArticleCluster]:
        """Create a cluster from a list of similar articles."""
        if not articles:
            return None
        
        # Find the most representative article (longest content, most recent)
        representative = max(articles, key=lambda a: (
            len(a.content) if a.content else 0,
            a.crawled_at.timestamp() if a.crawled_at else 0,
        ))
        
        # Generate cluster topic
        all_texts = [a.title + ' ' + a.summary + ' ' + a.content for a in articles]
        combined_text = ' '.join(all_texts)
        topic = self.text_processor.get_topic_from_text(combined_text, max_length=200)
        
        # Save representative article first
        representative.is_representative = True
        self.database.update_article(representative)
        
        # Create cluster
        cluster = ArticleCluster(
            topic=topic,
            representative_article_id=representative.id,
            article_count=len(articles),
        )
        
        cluster = self.database.save_cluster(cluster)
        
        # Assign articles to cluster
        for article in articles:
            article.cluster_id = cluster.id
            article.is_representative = (article.id == representative.id)
            self.database.update_article(article)
        
        return cluster
    
    def cluster_all(self, method: str = 'dbscan', batch_size: int = 100) -> Dict[str, Any]:
        """Cluster all articles using a specific clustering algorithm."""
        start_time = time.time()
        
        # Get all articles
        all_articles = self.database.get_all_articles()
        
        if not all_articles:
            return {
                'clusters_created': 0,
                'articles_clustered': 0,
                'elapsed_time': 0,
            }
        
        print(f"Clustering {len(all_articles)} articles using {method}...")
        
        if method == 'dbscan':
            result = self._cluster_with_dbscan(all_articles, batch_size)
        elif method == 'agglomerative':
            result = self._cluster_with_agglomerative(all_articles, batch_size)
        else:
            # Default to similarity-based
            result = self.deduplicate(batch_size)
        
        elapsed = time.time() - start_time
        result['elapsed_time'] = elapsed
        
        return result
    
    def _cluster_with_dbscan(self, articles: List[Article], batch_size: int = 100) -> Dict[str, Any]:
        """Cluster articles using DBSCAN."""
        # Extract texts
        texts = [a.title + ' ' + a.summary + ' ' + a.content for a in articles]
        
        # Vectorize
        vectors = self.text_processor.fit_transform(texts)
        
        # Find optimal epsilon based on similarity threshold
        # Convert similarity threshold to distance
        epsilon = 1 - self.similarity_threshold
        
        # Run DBSCAN
        dbscan = DBSCAN(eps=epsilon, min_samples=self.min_cluster_size, metric='cosine')
        labels = dbscan.fit_predict(vectors.toarray() if hasattr(vectors, 'toarray') else vectors)
        
        # Process clusters
        clusters_created = 0
        articles_clustered = 0
        
        for label in set(labels):
            if label == -1:  # Noise
                continue
            
            cluster_indices = [i for i, l in enumerate(labels) if l == label]
            cluster_articles = [articles[i] for i in cluster_indices]
            
            if len(cluster_articles) >= self.min_cluster_size:
                cluster = self._create_cluster(cluster_articles)
                if cluster:
                    clusters_created += 1
                    articles_clustered += len(cluster_articles)
        
        return {
            'clusters_created': clusters_created,
            'articles_clustered': articles_clustered,
        }
    
    def _cluster_with_agglomerative(self, articles: List[Article], batch_size: int = 100) -> Dict[str, Any]:
        """Cluster articles using Agglomerative Clustering."""
        # Extract texts
        texts = [a.title + ' ' + a.summary + ' ' + a.content for a in articles]
        
        # Vectorize
        vectors = self.text_processor.fit_transform(texts)
        
        # Determine number of clusters (estimate)
        n_clusters = max(2, len(articles) // 10)
        
        # Run Agglomerative Clustering
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            affinity='cosine',
            linkage='average',
        )
        labels = clustering.fit_predict(vectors.toarray() if hasattr(vectors, 'toarray') else vectors)
        
        # Process clusters
        clusters_created = 0
        articles_clustered = 0
        
        for label in set(labels):
            cluster_indices = [i for i, l in enumerate(labels) if l == label]
            cluster_articles = [articles[i] for i in cluster_indices]
            
            if len(cluster_articles) >= self.min_cluster_size:
                cluster = self._create_cluster(cluster_articles)
                if cluster:
                    clusters_created += 1
                    articles_clustered += len(cluster_articles)
        
        return {
            'clusters_created': clusters_created,
            'articles_clustered': articles_clustered,
        }
    
    def find_similar_articles(self, article_id: int, threshold: float = 0.8) -> List[Article]:
        """Find articles similar to a given article."""
        article = self.database.get_article_by_id(article_id)
        if not article:
            return []
        
        all_articles = self.database.get_all_articles()
        
        # Calculate similarity with all other articles
        target_text = article.title + ' ' + article.summary + ' ' + article.content
        similar_articles = []
        
        for other_article in all_articles:
            if other_article.id == article_id:
                continue
            
            other_text = other_article.title + ' ' + other_article.summary + ' ' + other_article.content
            similarity = self.text_processor.calculate_similarity(target_text, other_text)
            
            if similarity >= threshold:
                similar_articles.append((other_article, similarity))
        
        # Sort by similarity
        similar_articles.sort(key=lambda x: x[1], reverse=True)
        
        return [a for a, s in similar_articles]
    
    def get_cluster_articles(self, cluster_id: int) -> List[Article]:
        """Get all articles in a cluster."""
        return self.database.get_articles_by_cluster(cluster_id)
    
    def get_all_clusters(self) -> List[ArticleCluster]:
        """Get all clusters."""
        return self.database.get_all_clusters()
    
    def get_representative_articles(self, limit: int = 20) -> List[Article]:
        """Get representative articles from each cluster."""
        clusters = self.database.get_all_clusters()
        representatives = []
        
        for cluster in clusters:
            if cluster.representative_article_id:
                article = self.database.get_article_by_id(cluster.representative_article_id)
                if article:
                    representatives.append(article)
        
        # Sort by cluster updated date (most recent first)
        representatives.sort(
            key=lambda a: self.database.get_cluster_by_id(a.cluster_id).updated_at if a.cluster_id else datetime.min,
            reverse=True
        )
        
        return representatives[:limit]
    
    def reset_clusters(self) -> int:
        """Reset all cluster assignments."""
        articles = self.database.get_all_articles()
        
        for article in articles:
            if article.cluster_id:
                article.cluster_id = None
                article.is_representative = False
                self.database.update_article(article)
        
        # Delete all clusters
        clusters = self.database.get_all_clusters()
        for cluster in clusters:
            self.database.delete_cluster(cluster.id)
        
        return len(articles)
