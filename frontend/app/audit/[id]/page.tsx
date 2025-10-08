"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, RefreshCw, Download, Share2, Loader2, AlertCircle, ChevronDown } from 'lucide-react';
import ScoreDashboard from '../../components/ScoreDashboard';
import IssuePriorityList from '../../components/IssuePriorityList';
import SEOCopilot from '../../components/SEOCopilot';
import CopilotChatSidebar from '../../components/CopilotChatSidebar';
import { getAuditResults, getAuditStatus, AuditResults, AuditStatusResponse } from '../../lib/api';
import { downloadMarkdown, downloadPDF } from '../../lib/exportUtils';

export default function AuditResultsPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AuditResults | null>(null);
  const [status, setStatus] = useState<AuditStatusResponse | null>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);

  // Export handlers
  const handleExportMarkdown = () => {
    if (results) {
      downloadMarkdown(results);
      setShowExportMenu(false);
    }
  };

  const handleExportPDF = () => {
    if (results) {
      downloadPDF(results);
      setShowExportMenu(false);
    }
  };

  // Poll for status if not complete
  useEffect(() => {
    // eslint-disable-next-line prefer-const
    let pollInterval: NodeJS.Timeout | undefined;

    const fetchStatus = async () => {
      try {
        const statusData = await getAuditStatus(taskId);
        setStatus(statusData);

        if (statusData.status === 'complete') {
          // Fetch results
          const resultsData = await getAuditResults(taskId);
          setResults(resultsData);
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        } else if (statusData.status === 'failed') {
          setError(statusData.message || 'Audit failed');
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Error fetching audit status:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch audit status');
        setLoading(false);
        if (pollInterval) clearInterval(pollInterval);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 5 seconds if not complete
    pollInterval = setInterval(() => {
      if (status?.status !== 'complete' && status?.status !== 'failed') {
        fetchStatus();
      }
    }, 5000);

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  // Loading state
  if (loading && !status) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading audit results...</p>
        </div>
      </div>
    );
  }

  // In progress state
  if (status && status.status !== 'complete') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-6">
            <Loader2 className="w-16 h-16 animate-spin text-blue-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {status.status === 'crawling' ? 'Crawling Website...' : 'Processing Results...'}
            </h2>
            <p className="text-gray-600">This may take a few minutes</p>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>Progress</span>
              <span>{status.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${status.progress}%` }}
              />
            </div>
          </div>

          <button
            onClick={() => router.push('/')}
            className="mt-6 w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </button>
              <button
                onClick={() => router.push('/')}
                className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No results yet
  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/')}
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 mr-1" />
                Back
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900 truncate max-w-md">
                  {results.url}
                </h1>
                <p className="text-sm text-gray-500">
                  {new Date(results.timestamp).toLocaleDateString()} at{' '}
                  {new Date(results.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => window.location.reload()}
                className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Re-audit
              </button>

              {/* Export Dropdown */}
              <div className="relative">
                <button
                  className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  onClick={() => setShowExportMenu(!showExportMenu)}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export
                  <ChevronDown className="w-4 h-4 ml-1" />
                </button>

                {showExportMenu && (
                  <>
                    {/* Backdrop to close dropdown */}
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setShowExportMenu(false)}
                    />

                    {/* Dropdown Menu */}
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                      <button
                        onClick={handleExportMarkdown}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Export as Markdown
                      </button>
                      <button
                        onClick={handleExportPDF}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Export as PDF
                      </button>
                    </div>
                  </>
                )}
              </div>

              <button
                className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                  alert('Link copied to clipboard!');
                }}
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ScoreDashboard auditResults={results.score} />

        {/* Issue Priority List */}
        {results.issues && (
          <div className="mt-8">
            <IssuePriorityList issues={results.issues} />
          </div>
        )}
      </div>

      {/* SEO Copilot - Registers actions and provides context */}
      <SEOCopilot auditResults={results} />

      {/* Copilot Chat Sidebar */}
      <CopilotChatSidebar
        auditUrl={results.url}
        currentScore={results.score.total_score}
        maxScore={results.score.max_score}
      />
    </div>
  );
}
