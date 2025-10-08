/**
 * Content Strategy Types
 * Matches backend Pydantic models
 */

export enum ContentType {
  BLOG_POST = 'blog_post',
  GUIDE = 'guide',
  VIDEO = 'video',
  INFOGRAPHIC = 'infographic',
  CASE_STUDY = 'case_study',
  TOOL = 'tool',
  CHECKLIST = 'checklist',
  COMPARISON = 'comparison'
}

export enum Priority {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

export enum Difficulty {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard'
}

export enum ContentStatus {
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  DRAFT = 'draft',
  REVIEW = 'review',
  PUBLISHED = 'published'
}

export interface ContentPillar {
  id: string;
  name: string;
  description: string;
  keywords: string[];
  priority: Priority;
  total_opportunity: number;
  cluster_ids: number[];
}

export interface ContentItem {
  id: string;
  title: string;
  pillar_name: string;
  content_type: ContentType;
  target_keyword: string;
  supporting_keywords: string[];
  priority: Priority;
  estimated_difficulty: Difficulty;
  estimated_hours: number;
  scheduled_date: string;
  optimization_tips: string[];
  status: ContentStatus;
}

export interface ContentStrategy {
  seed_keyword: string;
  generated_at: string;
  pillars: ContentPillar[];
  content_items: ContentItem[];
  quick_wins: string[];
  implementation_notes: string;
  success_metrics: string[];
  total_pieces: number;
  estimated_total_hours: number;
  timeline_weeks: number;
}

export interface StrategyGenerationRequest {
  seed_keyword: string;
  timeline_weeks?: number;
  content_types?: ContentType[];
  max_pieces_per_week?: number;
}

export interface Competitor {
  domain: string;
  appearances: number;
  avg_position: number;
  keywords_ranked: string[];
  estimated_traffic: number;
  domain_authority: number;
  content_types: string[];
  strengths: string[];
  weaknesses: string[];
}

export interface CompetitiveAnalysisRequest {
  keywords: string[];
  max_competitors?: number;
}

export interface CalendarExport {
  format: 'ics' | 'csv';
  content: string;
}
