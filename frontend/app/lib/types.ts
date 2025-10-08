/**
 * Shared types for SERP-Master frontend
 */

export interface RecentAudit {
  id: string;
  url: string;
  timestamp: string;
  score?: number;
  status: 'complete' | 'failed' | 'in_progress';
}

export interface FormErrors {
  url?: string;
  maxPages?: string;
  general?: string;
}

export type AuditStatus = 'idle' | 'starting' | 'crawling' | 'processing' | 'complete' | 'error';
