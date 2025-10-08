"use client";

import { useState } from 'react';
import { NicheSearchForm } from '../components/niche-discovery/NicheSearchForm';
import { OpportunityGrid } from '../components/niche-discovery/OpportunityGrid';
import { ClusterVisualization } from '../components/niche-discovery/ClusterVisualization';
import { MarketAnalysisPanel } from '../components/niche-discovery/MarketAnalysisPanel';
import { ContentGapList } from '../components/niche-discovery/ContentGapList';
import { NicheDiscoveryAPI } from '../lib/api/niche-discovery';
import { NicheDiscoveryResponse } from '@/types/niche';
import { Loader2, Download, Share2 } from 'lucide-react';

export default function NicheDiscoveryPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<NicheDiscoveryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('opportunities');

  const handleSearch = async (seedKeyword: string, filters: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await NicheDiscoveryAPI.analyzeNiche({
        seed_keyword: seedKeyword,
        filters,
        limit: 50,
        include_trends: false,
      });

      setResults(response);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze niche');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = () => {
    if (!results) return;

    // Create CSV export
    const csv = [
      ['Keyword', 'Score', 'Volume', 'Difficulty', 'CPC', 'Level'].join(','),
      ...results.opportunities.map(opp =>
        [opp.keyword, opp.opportunity_score, opp.search_volume, opp.keyword_difficulty, opp.cpc, opp.opportunity_level].join(',')
      )
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${results.seed_keyword}-opportunities.csv`;
    a.click();
  };

  const tabs = [
    { id: 'opportunities', label: 'Opportunities' },
    { id: 'clusters', label: 'Clusters' },
    { id: 'market', label: 'Market Analysis' },
    { id: 'gaps', label: 'Content Gaps' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🔍 Niche Discovery Engine
          </h1>
          <p className="text-xl text-gray-600">
            Find profitable keyword opportunities and content gaps in any niche
          </p>
        </div>

        {/* Search Form */}
        <div className="mb-12">
          <NicheSearchForm onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="h-16 w-16 text-blue-600 animate-spin mb-4" />
            <p className="text-xl font-semibold text-gray-900">Analyzing niche...</p>
            <p className="text-gray-600 mt-2">This may take 10-20 seconds</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-bold text-red-900 mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && !isLoading && (
          <div className="space-y-8">
            {/* Summary Bar */}
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Results for "{results.seed_keyword}"
                  </h2>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>📊 {results.summary.total_keywords} keywords</span>
                    <span>•</span>
                    <span>🎯 {results.summary.total_clusters} clusters</span>
                    <span>•</span>
                    <span>💎 {results.opportunities.length} opportunities</span>
                    <span>•</span>
                    <span className="font-semibold text-blue-600">
                      {Math.round(results.summary.confidence_score * 100)}% confidence
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleExport}
                    className="px-4 py-2 bg-white border-2 border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Export CSV
                  </button>

                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2">
                    <Share2 className="h-4 w-4" />
                    Share
                  </button>
                </div>
              </div>
            </div>

            {/* Custom Tabs */}
            <div className="w-full">
              {/* Tab Buttons */}
              <div className="grid grid-cols-4 gap-2 mb-8 bg-white rounded-lg p-2 border-2 border-gray-200">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div>
                {activeTab === 'opportunities' && (
                  <OpportunityGrid opportunities={results.opportunities} />
                )}

                {activeTab === 'clusters' && (
                  <ClusterVisualization clusters={results.clusters} />
                )}

                {activeTab === 'market' && (
                  <MarketAnalysisPanel analysis={results.niche_analysis} />
                )}

                {activeTab === 'gaps' && (
                  <ContentGapList gaps={results.niche_analysis.content_gaps} />
                )}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!results && !isLoading && !error && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🎯</div>
            <p className="text-xl text-gray-600">
              Enter a seed keyword above to discover niche opportunities
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
