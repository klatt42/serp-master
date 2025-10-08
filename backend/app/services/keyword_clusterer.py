"""
Keyword Clustering Service
Groups related keywords using semantic similarity and ML clustering
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from typing import List, Dict, Optional
from collections import Counter
import re
import logging

from app.models.keyword import KeywordData
from app.models.cluster import KeywordCluster, ClusterTheme

logger = logging.getLogger(__name__)


class KeywordClusterer:
    """
    Clusters keywords using TF-IDF vectorization and ML clustering
    """

    def __init__(self, min_cluster_size: int = 3, max_clusters: int = 15):
        """
        Initialize clusterer with parameters

        Args:
            min_cluster_size: Minimum keywords per cluster
            max_clusters: Maximum number of clusters to create
        """
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)  # Unigrams to trigrams
        )

    def cluster_keywords(
        self,
        keywords: List[KeywordData],
        method: str = "kmeans"
    ) -> List[KeywordCluster]:
        """
        Cluster keywords into semantic groups

        Args:
            keywords: List of keywords to cluster
            method: Clustering method ('kmeans')

        Returns:
            List of keyword clusters with metadata
        """
        if len(keywords) < self.min_cluster_size:
            # Not enough keywords to cluster meaningfully
            logger.info(f"Only {len(keywords)} keywords, creating single cluster")
            return [self._create_single_cluster(keywords)]

        # Step 1: Extract keyword text
        keyword_texts = [kw.keyword for kw in keywords]

        # Step 2: Vectorize using TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform(keyword_texts)
            logger.info(f"Vectorized {len(keyword_texts)} keywords into TF-IDF matrix")
        except Exception as e:
            logger.error(f"Error vectorizing keywords: {e}")
            return [self._create_single_cluster(keywords)]

        # Step 3: Determine optimal number of clusters
        n_clusters = self._determine_optimal_clusters(tfidf_matrix, keywords)
        logger.info(f"Determined optimal clusters: {n_clusters}")

        # Step 4: Perform clustering
        if method == "kmeans":
            cluster_labels = self._kmeans_clustering(tfidf_matrix, n_clusters)
        else:
            cluster_labels = self._kmeans_clustering(tfidf_matrix, n_clusters)

        # Step 5: Group keywords by cluster label
        clusters = self._group_by_cluster(keywords, cluster_labels)
        logger.info(f"Grouped into {len(clusters)} clusters")

        # Step 6: Generate cluster metadata
        enriched_clusters = []
        for cluster_data in clusters:
            cluster = self._enrich_cluster(cluster_data)
            enriched_clusters.append(cluster)

        # Step 7: Sort by importance (total search volume)
        enriched_clusters.sort(key=lambda c: c.total_search_volume, reverse=True)

        return enriched_clusters

    def _determine_optimal_clusters(
        self,
        tfidf_matrix: np.ndarray,
        keywords: List[KeywordData]
    ) -> int:
        """
        Determine optimal number of clusters using elbow method
        """
        n_samples = tfidf_matrix.shape[0]

        # Can't have more clusters than samples
        max_k = min(self.max_clusters, n_samples // self.min_cluster_size)
        max_k = max(2, max_k)  # At least 2 clusters

        if max_k <= 2:
            return 2

        # Test different cluster counts
        silhouette_scores = []

        for k in range(2, max_k + 1):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(tfidf_matrix)

                # Calculate silhouette score if enough samples
                if n_samples > k:
                    score = silhouette_score(tfidf_matrix, labels)
                    silhouette_scores.append(score)
                else:
                    silhouette_scores.append(0)
            except Exception as e:
                logger.warning(f"Error calculating silhouette for k={k}: {e}")
                silhouette_scores.append(0)

        # Find best k
        if silhouette_scores and max(silhouette_scores) > 0:
            best_k = silhouette_scores.index(max(silhouette_scores)) + 2
        else:
            best_k = max(2, min(5, max_k))  # Default to 5 or less

        return best_k

    def _kmeans_clustering(self, tfidf_matrix: np.ndarray, n_clusters: int) -> np.ndarray:
        """Perform K-means clustering"""
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(tfidf_matrix)
            return labels
        except Exception as e:
            logger.error(f"K-means clustering failed: {e}")
            # Return all zeros if clustering fails
            return np.zeros(tfidf_matrix.shape[0], dtype=int)

    def _group_by_cluster(
        self,
        keywords: List[KeywordData],
        cluster_labels: np.ndarray
    ) -> List[Dict]:
        """Group keywords by their cluster label"""
        cluster_dict = {}

        for keyword, label in zip(keywords, cluster_labels):
            if label not in cluster_dict:
                cluster_dict[label] = []
            cluster_dict[label].append(keyword)

        # Convert to list of cluster data
        clusters = [{"keywords": kws, "label": label} for label, kws in cluster_dict.items()]

        # Filter out small clusters
        clusters = [c for c in clusters if len(c["keywords"]) >= self.min_cluster_size]

        return clusters

    def _enrich_cluster(self, cluster_data: Dict) -> KeywordCluster:
        """Add metadata and analysis to cluster"""
        keywords = cluster_data["keywords"]
        label = cluster_data["label"]

        # Calculate aggregate statistics
        total_volume = sum(kw.search_volume for kw in keywords)
        avg_volume = total_volume // len(keywords) if keywords else 0

        difficulties = [kw.keyword_difficulty for kw in keywords if kw.keyword_difficulty]
        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 50

        cpcs = [kw.cpc for kw in keywords if kw.cpc]
        avg_cpc = sum(cpcs) / len(cpcs) if cpcs else 0

        # Determine primary intent
        intents = []
        for kw in keywords:
            if kw.intent:
                intent_val = kw.intent.value if hasattr(kw.intent, 'value') else kw.intent
                intents.append(intent_val)
        primary_intent = Counter(intents).most_common(1)[0][0] if intents else "informational"

        # Generate cluster theme
        theme = self._generate_cluster_theme(keywords)

        # Generate cluster name
        cluster_name = self._generate_cluster_name(keywords, theme)

        # Extract common SERP features
        all_features = []
        for kw in keywords:
            all_features.extend(kw.serp_features)
        common_features = [f[0] for f in Counter(all_features).most_common(3)]

        return KeywordCluster(
            cluster_id=label,
            cluster_name=cluster_name,
            theme=theme,
            keywords=[kw.keyword for kw in keywords],
            total_keywords=len(keywords),
            total_search_volume=total_volume,
            avg_search_volume=avg_volume,
            avg_difficulty=round(avg_difficulty, 2),
            avg_cpc=round(avg_cpc, 2),
            primary_intent=primary_intent,
            common_serp_features=common_features
        )

    def _generate_cluster_theme(self, keywords: List[KeywordData]) -> ClusterTheme:
        """
        Generate semantic theme for cluster
        Uses word frequency and keyword analysis
        """
        # Extract all words from keywords
        all_words = []
        for kw in keywords:
            words = re.findall(r'\b\w+\b', kw.keyword.lower())
            all_words.extend(words)

        # Remove common words
        stop_words = {'seo', 'best', 'top', 'how', 'what', 'the', 'for', 'and', 'or', 'in', 'to', 'of', 'a', 'an', 'is', 'are', 'was', 'were'}
        filtered_words = [w for w in all_words if w not in stop_words and len(w) > 2]

        # Find most common meaningful words
        word_freq = Counter(filtered_words)
        top_words = [w[0] for w in word_freq.most_common(3)]

        # Classify theme type
        theme_type = self._classify_theme_type(keywords, top_words)

        return ClusterTheme(
            theme_type=theme_type,
            key_terms=top_words,
            description=self._describe_theme(theme_type, top_words)
        )

    def _classify_theme_type(self, keywords: List[KeywordData], top_words: List[str]) -> str:
        """Classify the type of content theme"""
        # Analyze keywords to determine theme
        all_text = " ".join([kw.keyword for kw in keywords]).lower()

        if any(word in all_text for word in ['tool', 'software', 'app', 'platform']):
            return "tools_and_software"
        elif any(word in all_text for word in ['how', 'guide', 'tutorial', 'learn']):
            return "educational_content"
        elif any(word in all_text for word in ['best', 'top', 'review', 'comparison']):
            return "comparison_and_review"
        elif any(word in all_text for word in ['service', 'agency', 'company', 'hire']):
            return "services"
        elif any(word in all_text for word in ['tips', 'strategies', 'tactics', 'ideas']):
            return "strategies_and_tactics"
        else:
            return "general_information"

    def _describe_theme(self, theme_type: str, key_terms: List[str]) -> str:
        """Generate human-readable theme description"""
        theme_descriptions = {
            "tools_and_software": f"Software and tools related to {', '.join(key_terms)}",
            "educational_content": f"Educational content about {', '.join(key_terms)}",
            "comparison_and_review": f"Comparisons and reviews of {', '.join(key_terms)}",
            "services": f"Professional services for {', '.join(key_terms)}",
            "strategies_and_tactics": f"Strategies and tactics for {', '.join(key_terms)}",
            "general_information": f"General information about {', '.join(key_terms)}"
        }

        return theme_descriptions.get(theme_type, f"Content about {', '.join(key_terms)}")

    def _generate_cluster_name(self, keywords: List[KeywordData], theme: ClusterTheme) -> str:
        """Generate descriptive name for cluster"""
        # Use most common significant words
        if len(theme.key_terms) >= 2:
            return f"{theme.key_terms[0].title()} {theme.key_terms[1].title()}"
        elif len(theme.key_terms) == 1:
            return theme.key_terms[0].title()
        else:
            # Fallback: use first keyword
            return keywords[0].keyword[:30] if keywords else "Cluster"

    def _create_single_cluster(self, keywords: List[KeywordData]) -> KeywordCluster:
        """Create a single cluster when clustering isn't possible"""
        total_volume = sum(kw.search_volume for kw in keywords)

        return KeywordCluster(
            cluster_id=0,
            cluster_name="All Keywords",
            theme=ClusterTheme(
                theme_type="general",
                key_terms=[],
                description="All discovered keywords"
            ),
            keywords=[kw.keyword for kw in keywords],
            total_keywords=len(keywords),
            total_search_volume=total_volume,
            avg_search_volume=total_volume // len(keywords) if keywords else 0,
            avg_difficulty=50,
            avg_cpc=0,
            primary_intent="informational",
            common_serp_features=[]
        )
