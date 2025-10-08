export interface ClusterTheme {
  theme_type: string;
  key_terms: string[];
  description: string;
}

export interface KeywordCluster {
  cluster_id: number;
  cluster_name: string;
  theme: ClusterTheme;
  keywords: string[];
  total_keywords: number;
  total_search_volume: number;
  avg_search_volume: number;
  avg_difficulty: number;
  avg_cpc: number;
  primary_intent: string;
  common_serp_features: string[];
}

export interface ClusterAnalysis {
  seed_keyword: string;
  total_clusters: number;
  clusters: KeywordCluster[];
  unclustered_keywords: number;
  analysis_summary: Record<string, any>;
}
