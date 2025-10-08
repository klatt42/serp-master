/**
 * API client for SERP-Master backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface AuditStartResponse {
  task_id: string;
  status: 'crawling' | 'processing' | 'complete' | 'failed';
  estimated_time_seconds: number;
}

export interface AuditStatusResponse {
  task_id: string;
  status: 'crawling' | 'processing' | 'complete' | 'failed';
  progress: number;
  message?: string;
}

export interface Issue {
  id: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  title: string;
  description: string;
  pages_affected: number;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  recommendation: string;
  quick_win: boolean;
  category: 'SEO' | 'AEO' | 'GEO';
  details?: {
    explanation: string;
    fix_steps: string[];
    code_example?: string;
  };
}

export interface AuditResults {
  task_id: string;
  url: string;
  timestamp: string;
  score: {
    total_score: number;
    max_score: number;
    percentage: number;
    grade: string;
    component_scores: {
      seo: { score: number; max: number; percentage: number };
      aeo: { score: number; max: number; percentage: number };
      geo: { score: number; max: number; percentage: number };
    };
  };
  seo_score: Record<string, unknown>;
  aeo_score: Record<string, unknown>;
  geo_score: Record<string, unknown>;
  issues?: {
    critical: Issue[];
    warnings: Issue[];
    info: Issue[];
    quick_wins: Issue[];
  };
  quick_wins?: Array<{
    title: string;
    impact: string;
    effort: string;
    points: number;
    description: string;
  }>;
  metadata: Record<string, unknown>;
}

/**
 * Start a new website audit
 */
export async function startAudit(url: string, maxPages: number = 50): Promise<AuditStartResponse> {
  const response = await apiClient.post<AuditStartResponse>('/api/audit/start', {
    url,
    max_pages: maxPages,
  });
  return response.data;
}

/**
 * Check audit status
 */
export async function getAuditStatus(taskId: string): Promise<AuditStatusResponse> {
  const response = await apiClient.get<AuditStatusResponse>(`/api/audit/status/${taskId}`);
  return response.data;
}

/**
 * Get audit results
 */
export async function getAuditResults(taskId: string): Promise<AuditResults> {
  const response = await apiClient.get<AuditResults>(`/api/audit/results/${taskId}`);
  return response.data;
}

/**
 * Get quick wins for an audit
 */
export async function getQuickWins(taskId: string) {
  const response = await apiClient.get(`/api/audit/quick-wins/${taskId}`);
  return response.data;
}

/**
 * Poll audit status until complete
 */
export async function pollAuditStatus(
  taskId: string,
  onProgress?: (status: AuditStatusResponse) => void,
  intervalMs: number = 5000,
  timeoutMs: number = 600000 // 10 minutes
): Promise<AuditStatusResponse> {
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getAuditStatus(taskId);

        if (onProgress) {
          onProgress(status);
        }

        // Check if complete
        if (status.status === 'complete') {
          resolve(status);
          return;
        }

        // Check if failed
        if (status.status === 'failed') {
          reject(new Error(status.message || 'Audit failed'));
          return;
        }

        // Check timeout
        if (Date.now() - startTime > timeoutMs) {
          reject(new Error('Audit timeout'));
          return;
        }

        // Continue polling
        setTimeout(poll, intervalMs);
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    const urlObj = new URL(url.startsWith('http') ? url : `https://${url}`);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    return false;
  }
}

/**
 * Normalize URL (add https if missing)
 */
export function normalizeUrl(url: string): string {
  url = url.trim();
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`;
  }
  return url;
}

// ============================================================================
// Week 4: Competitor Comparison API Functions
// ============================================================================

export interface ComparisonStartResponse {
  comparison_id: string;
  status: 'crawling' | 'analyzing' | 'complete' | 'failed';
  sites_to_analyze: number;
  estimated_time_seconds: number;
}

export interface ComparisonStatusResponse {
  comparison_id: string;
  status: 'crawling' | 'analyzing' | 'complete' | 'failed';
  progress: number;
  sites_completed: number;
  sites_total: number;
  message?: string;
}

export interface SiteComparisonData {
  url: string;
  total_score: number;
  rank: number;
  scores: Record<string, unknown>;
}

export interface CompetitiveGap {
  dimension: string;
  issue: string;
  user_score: number;
  competitor_score: number;
  competitor_url: string;
  gap: number;
  category: string;
  priority: string;
}

export interface CompetitiveAction {
  action: string;
  description: string;
  dimension: string;
  impact: number;
  effort: string;
  beats: string[];
  current_rank: number;
  potential_rank: number;
  priority: string;
  related_competitor: string;
}

export interface CompetitorQuickWin {
  fix: string;
  description: string;
  beats: string[];
  impact: number;
  effort: string;
  dimension: string;
  rank_improvement: number;
}

export interface ComparisonResults {
  comparison_id: string;
  user_site: SiteComparisonData;
  competitors: SiteComparisonData[];
  comparison: {
    user_rank: number;
    total_sites: number;
    user_score: number;
    highest_competitor_score: number;
    lowest_competitor_score: number;
    average_competitor_score: number;
    score_gap_to_first: number;
    rankings: Array<{
      rank: number;
      url: string;
      score: number;
    }>;
  };
  gaps: CompetitiveGap[];
  competitive_strategy: CompetitiveAction[];
  quick_wins: CompetitorQuickWin[];
  analysis_date: string;
  sites_analyzed: number;
}

/**
 * Start a new competitor comparison
 */
export async function startComparison(
  userUrl: string,
  competitorUrls: string[],
  maxPages: number = 50
): Promise<ComparisonStartResponse> {
  const response = await apiClient.post<ComparisonStartResponse>('/api/compare/start', {
    user_url: userUrl,
    competitor_urls: competitorUrls,
    max_pages: maxPages,
  });
  return response.data;
}

/**
 * Check comparison status
 */
export async function getComparisonStatus(comparisonId: string): Promise<ComparisonStatusResponse> {
  const response = await apiClient.get<ComparisonStatusResponse>(`/api/compare/status/${comparisonId}`);
  return response.data;
}

/**
 * Get comparison results
 */
export async function getComparisonResults(comparisonId: string): Promise<ComparisonResults> {
  const response = await apiClient.get<ComparisonResults>(`/api/compare/results/${comparisonId}`);
  return response.data;
}

/**
 * Poll comparison status until complete
 */
export async function pollComparisonStatus(
  comparisonId: string,
  onProgress?: (status: ComparisonStatusResponse) => void,
  intervalMs: number = 5000,
  timeoutMs: number = 900000 // 15 minutes (longer for multiple sites)
): Promise<ComparisonStatusResponse> {
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getComparisonStatus(comparisonId);

        if (onProgress) {
          onProgress(status);
        }

        // Check if complete
        if (status.status === 'complete') {
          resolve(status);
          return;
        }

        // Check if failed
        if (status.status === 'failed') {
          reject(new Error(status.message || 'Comparison failed'));
          return;
        }

        // Check timeout
        if (Date.now() - startTime > timeoutMs) {
          reject(new Error('Comparison timeout'));
          return;
        }

        // Continue polling
        setTimeout(poll, intervalMs);
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}
