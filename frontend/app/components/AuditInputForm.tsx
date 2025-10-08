"use client";

import { useState, useEffect, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Search, AlertCircle, Loader2, ChevronDown, ChevronUp, Clock, TrendingUp } from 'lucide-react';
import { startAudit, pollAuditStatus, isValidUrl, normalizeUrl } from '../lib/api';
import { RecentAudit, FormErrors, AuditStatus } from '../lib/types';

export default function AuditInputForm() {
  const router = useRouter();

  // Form state
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState(50);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Status state
  const [status, setStatus] = useState<AuditStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [errors, setErrors] = useState<FormErrors>({});
  const [taskId, setTaskId] = useState<string | null>(null);

  // Recent audits
  const [recentAudits, setRecentAudits] = useState<RecentAudit[]>([]);

  // Load recent audits from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('recentAudits');
    if (stored) {
      try {
        setRecentAudits(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to load recent audits:', e);
      }
    }
  }, []);

  // Save recent audit to localStorage
  const saveRecentAudit = (audit: RecentAudit) => {
    const updated = [audit, ...recentAudits.filter(a => a.id !== audit.id)].slice(0, 5);
    setRecentAudits(updated);
    localStorage.setItem('recentAudits', JSON.stringify(updated));
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Validate URL
    if (!url.trim()) {
      newErrors.url = 'Please enter a URL';
    } else if (!isValidUrl(url)) {
      newErrors.url = 'Please enter a valid URL (e.g., example.com or https://example.com)';
    }

    // Validate max pages
    if (maxPages < 10 || maxPages > 100) {
      newErrors.maxPages = 'Max pages must be between 10 and 100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const normalizedUrl = normalizeUrl(url);

    try {
      setStatus('starting');
      setProgress(0);
      setErrors({});

      // Start the audit
      const response = await startAudit(normalizedUrl, maxPages);
      setTaskId(response.task_id);
      setStatus('crawling');

      // Save to recent audits
      const newAudit: RecentAudit = {
        id: response.task_id,
        url: normalizedUrl,
        timestamp: new Date().toISOString(),
        status: 'in_progress',
      };
      saveRecentAudit(newAudit);

      // Poll for status updates
      await pollAuditStatus(
        response.task_id,
        (statusUpdate) => {
          setProgress(statusUpdate.progress);

          if (statusUpdate.status === 'processing') {
            setStatus('processing');
          }
        }
      );

      // Audit complete - navigate to results
      setStatus('complete');
      router.push(`/audit/${response.task_id}`);

    } catch (error) {
      console.error('Audit failed:', error);
      setStatus('error');
      const errorMessage = error instanceof Error
        ? error.message
        : 'Failed to start audit. Please try again.';
      setErrors({
        general: errorMessage,
      });

      // Update recent audit status
      if (taskId) {
        const updated = recentAudits.map(a =>
          a.id === taskId ? { ...a, status: 'failed' as const } : a
        );
        setRecentAudits(updated);
        localStorage.setItem('recentAudits', JSON.stringify(updated));
      }
    }
  };

  // View recent audit results
  const viewAudit = (auditId: string) => {
    router.push(`/audit/${auditId}`);
  };

  // Get status message
  const getStatusMessage = () => {
    switch (status) {
      case 'starting':
        return 'Starting audit...';
      case 'crawling':
        return 'Crawling website...';
      case 'processing':
        return 'Analyzing results...';
      case 'complete':
        return 'Complete! Redirecting...';
      case 'error':
        return 'Error occurred';
      default:
        return '';
    }
  };

  const isLoading = ['starting', 'crawling', 'processing'].includes(status);

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Main Form Card */}
      <div className="bg-white rounded-lg shadow-lg p-6 md:p-8 animate-slide-up">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* URL Input */}
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              Website URL
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="url"
                type="text"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (errors.url) {
                    setErrors({ ...errors, url: undefined });
                  }
                }}
                disabled={isLoading}
                placeholder="example.com or https://example.com"
                className={`block w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                  errors.url
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300 bg-white'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              />
            </div>
            {errors.url && (
              <div className="mt-2 flex items-center text-sm text-red-600 animate-fade-in">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.url}
              </div>
            )}
          </div>

          {/* Advanced Options Toggle */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            disabled={isLoading}
            className="flex items-center text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          >
            {showAdvanced ? (
              <>
                <ChevronUp className="h-4 w-4 mr-1" />
                Hide advanced options
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-1" />
                Show advanced options
              </>
            )}
          </button>

          {/* Advanced Options */}
          {showAdvanced && (
            <div className="bg-gray-50 rounded-lg p-4 space-y-4 animate-slide-down">
              <div>
                <label htmlFor="maxPages" className="block text-sm font-medium text-gray-700 mb-2">
                  Maximum pages to crawl
                </label>
                <input
                  id="maxPages"
                  type="number"
                  min="10"
                  max="100"
                  value={maxPages}
                  onChange={(e) => {
                    setMaxPages(parseInt(e.target.value) || 50);
                    if (errors.maxPages) {
                      setErrors({ ...errors, maxPages: undefined });
                    }
                  }}
                  disabled={isLoading}
                  className={`block w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.maxPages ? 'border-red-300' : 'border-gray-300'
                  } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                />
                {errors.maxPages && (
                  <p className="mt-1 text-sm text-red-600 animate-fade-in">{errors.maxPages}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Recommended: 50 pages for comprehensive analysis
                </p>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full flex items-center justify-center px-6 py-3 rounded-lg font-medium text-white transition-all transform hover:scale-[1.02] ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl'
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin h-5 w-5 mr-2" />
                {getStatusMessage()}
              </>
            ) : (
              <>
                <Search className="h-5 w-5 mr-2" />
                Start Audit
              </>
            )}
          </button>

          {/* Progress Bar */}
          {isLoading && (
            <div className="space-y-2 animate-fade-in">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>{getStatusMessage()}</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* General Error */}
          {errors.general && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 animate-fade-in">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="mt-1 text-sm text-red-700">{errors.general}</p>
                  <button
                    type="button"
                    onClick={() => setErrors({ ...errors, general: undefined })}
                    className="mt-2 text-sm font-medium text-red-600 hover:text-red-700"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Recent Audits */}
      {recentAudits.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6 animate-slide-up">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Clock className="h-5 w-5 mr-2 text-gray-500" />
            Recent Audits
          </h3>
          <div className="space-y-3">
            {recentAudits.map((audit) => (
              <div
                key={audit.id}
                className="flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer group"
                onClick={() => viewAudit(audit.id)}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {audit.url}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(audit.timestamp).toLocaleDateString()} at{' '}
                    {new Date(audit.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  {audit.score !== undefined && (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {audit.score}/100
                    </span>
                  )}
                  <TrendingUp className="h-4 w-4 text-gray-400 group-hover:text-blue-600 transition-colors" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State for Recent Audits */}
      {recentAudits.length === 0 && !isLoading && (
        <div className="text-center py-8 text-gray-500 animate-fade-in">
          <p className="text-sm">No recent audits. Start your first audit above!</p>
        </div>
      )}
    </div>
  );
}
