export type OpportunityLevel = 'excellent' | 'good' | 'moderate' | 'low';

export interface KeywordOpportunity {
  keyword: string;
  search_volume: number;
  keyword_difficulty: number;
  cpc: number;
  competition: number;

  // Scores
  volume_score: number;
  difficulty_score: number;
  cpc_score: number;
  competition_score: number;
  opportunity_score: number;
  roi_potential: number;

  opportunity_level: OpportunityLevel;
  recommended_content_type: string;
  estimated_traffic: number;
  effort_level: string;
}

export interface OpportunityFilters {
  min_volume?: number;
  max_difficulty?: number;
  min_cpc?: number;
  max_cpc?: number;
  intents?: string[];
}
