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
