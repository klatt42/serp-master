"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Loader2, AlertCircle, Target, Zap, Download, ChevronDown } from 'lucide-react';
import { getComparisonResults, getComparisonStatus, ComparisonResults, ComparisonStatusResponse } from '../../lib/api';
import { downloadComparisonMarkdown, downloadComparisonPDF } from '../../lib/exportUtils';

export default function ComparisonResultsPage() {
  const params = useParams();
  const router = useRouter();
  const comparisonId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ComparisonResults | null>(null);
  const [status, setStatus] = useState<ComparisonStatusResponse | null>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);

  // Export handlers
  const handleExportMarkdown = () => {
    if (results) {
      downloadComparisonMarkdown(results);
      setShowExportMenu(false);
    }
  };

  const handleExportPDF = () => {
    if (results) {
      downloadComparisonPDF(results);
      setShowExportMenu(false);
    }
  };

  // Poll for status
  useEffect(() => {
    let pollInterval: NodeJS.Timeout | undefined;

    const fetchStatus = async () => {
      try {
        const statusData = await getComparisonStatus(comparisonId);
        setStatus(statusData);

        if (statusData.status === 'complete') {
          const resultsData = await getComparisonResults(comparisonId);
          setResults(resultsData);
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        } else if (statusData.status === 'failed') {
          setError(statusData.message || 'Comparison failed');
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Error fetching comparison:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch comparison');
        setLoading(false);
        if (pollInterval) clearInterval(pollInterval);
      }
    };

    fetchStatus();
    pollInterval = setInterval(() => {
      if (status?.status !== 'complete' && status?.status !== 'failed') {
        fetchStatus();
      }
    }, 5000);

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [comparisonId]);

  // Loading state
  if (loading && !status) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading comparison...</p>
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
              {status.status === 'crawling' ? 'Crawling Websites...' : 'Analyzing Competition...'}
            </h2>
            <p className="text-gray-600">
              {status.sites_completed} of {status.sites_total} sites completed
            </p>
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
            onClick={() => router.push('/compare')}
            className="mt-6 w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
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
            <button
              onClick={() => router.push('/compare')}
              className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Comparison Form
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push('/compare')}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              Back to Comparison Form
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
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Rankings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">Competitive Rankings</h2>
          <div className="space-y-3">
            {results.comparison.rankings.map((site, index) => (
              <div
                key={site.url}
                className={`flex items-center justify-between p-4 rounded-lg ${
                  site.url === results.user_site.url ? 'bg-blue-50 border-2 border-blue-500' : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <span className="text-2xl font-bold text-gray-400">#{site.rank}</span>
                  <div>
                    <p className="font-medium">{site.url}</p>
                    {site.url === results.user_site.url && (
                      <span className="text-xs text-blue-600 font-semibold">Your Site</span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">{site.score}</p>
                  <p className="text-sm text-gray-500">points</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gaps */}
        {results.gaps.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <Target className="w-6 h-6 mr-2 text-orange-600" />
              Competitive Gaps
            </h2>
            <div className="space-y-3">
              {results.gaps.slice(0, 5).map((gap, index) => (
                <div key={index} className="p-4 bg-orange-50 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-semibold rounded ${
                          gap.priority === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {gap.priority.toUpperCase()}
                        </span>
                        <span className="text-xs font-medium text-gray-600">{gap.dimension}</span>
                      </div>
                      <p className="mt-2 font-medium">{gap.issue}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        vs {gap.competitor_url}
                      </p>
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-2xl font-bold text-orange-600">+{gap.gap}</p>
                      <p className="text-xs text-gray-500">pts gap</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Wins */}
        {results.quick_wins.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <Zap className="w-6 h-6 mr-2 text-yellow-500" />
              Quick Wins
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.quick_wins.map((win, index) => (
                <div key={index} className="p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-yellow-800 bg-yellow-100 px-2 py-1 rounded">
                      {win.dimension}
                    </span>
                    <span className="text-sm font-bold text-green-600">
                      ↑ {win.rank_improvement} rank{win.rank_improvement > 1 ? 's' : ''}
                    </span>
                  </div>
                  <p className="font-medium text-gray-900 mb-2">{win.fix}</p>
                  <p className="text-sm text-gray-600 mb-2">{win.description}</p>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">Impact: +{win.impact} pts</span>
                    <span className="text-gray-500">Effort: {win.effort}</span>
                  </div>
                  {win.beats.length > 0 && (
                    <p className="mt-2 text-xs text-blue-600">
                      Beats: {win.beats.join(', ')}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Strategy */}
        {results.competitive_strategy.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Competitive Strategy</h2>
            <div className="space-y-3">
              {results.competitive_strategy.slice(0, 5).map((action, index) => (
                <div key={index} className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{action.action}</h3>
                      <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                        <span>Impact: +{action.impact} pts</span>
                        <span>Effort: {action.effort}</span>
                        <span>Rank: {action.current_rank} → {action.potential_rank}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
