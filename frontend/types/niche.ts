import { KeywordOpportunity } from './opportunity';
import { KeywordCluster } from './cluster';

export type MarketSize = 'small' | 'medium' | 'large' | 'huge';
export type CompetitionLevel = 'low' | 'medium' | 'high' | 'very_high';

export interface ContentGap {
  gap_type: string;
  description: string;
  keywords: string[];
  estimated_impact: string;
  priority: string;
}

export interface MarketOpportunity {
  cluster_name: string;
  cluster_theme: string;
  opportunity_score: number;
  opportunity_level: string;
  total_search_volume: number;
  avg_difficulty: number;
  recommended_action: string;
}

export interface NicheAnalysis {
  seed_keyword: string;
  total_keywords: number;
  total_search_volume: number;
  market_size: MarketSize;
  competition_level: CompetitionLevel;
  avg_keyword_difficulty: number;
  monetization_potential: number;
  top_serp_features: string[];
  content_gaps: ContentGap[];
  recommended_strategy: string;
  confidence_score: number;
  opportunities: MarketOpportunity[];
  cluster_count: number;
}

export interface NicheDiscoveryResponse {
  seed_keyword: string;
  opportunities: KeywordOpportunity[];
  clusters: KeywordCluster[];
  niche_analysis: NicheAnalysis;
  summary: {
    total_keywords: number;
    total_clusters: number;
    market_size: MarketSize;
    competition_level: CompetitionLevel;
    confidence_score: number;
  };
}

export interface NicheDiscoveryRequest {
  seed_keyword: string;
  filters?: {
    min_volume?: number;
    max_difficulty?: number;
    min_cpc?: number;
    max_cpc?: number;
    intents?: string[];
  };
  limit?: number;
  include_trends?: boolean;
}
