/**
 * Competitor Analysis Component
 * Displays competitive intelligence dashboard
 */

import React from 'react';
import { Competitor } from '@/types/strategy';
import CompetitorCard from './CompetitorCard';
import { Users, TrendingUp, Target } from 'lucide-react';

interface CompetitorAnalysisProps {
  competitors: Competitor[];
  isLoading?: boolean;
}

export default function CompetitorAnalysis({ competitors, isLoading }: CompetitorAnalysisProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (competitors.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <Users className="h-12 w-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-500">No competitor data available yet.</p>
      </div>
    );
  }

  // Calculate aggregate metrics
  const totalKeywords = new Set(competitors.flatMap(c => c.keywords_ranked)).size;
  const avgPosition = competitors.reduce((sum, c) => sum + c.avg_position, 0) / competitors.length;
  const totalTraffic = competitors.reduce((sum, c) => sum + c.estimated_traffic, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-2 flex items-center">
          <Users className="h-7 w-7 mr-2" />
          Competitive Intelligence
        </h2>
        <p className="text-blue-100">
          Analyzing {competitors.length} top competitors in your niche
        </p>
      </div>

      {/* Aggregate Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Competitors</p>
              <p className="text-3xl font-bold text-gray-900">{competitors.length}</p>
            </div>
            <Users className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Unique Keywords</p>
              <p className="text-3xl font-bold text-gray-900">{totalKeywords}</p>
            </div>
            <Target className="h-10 w-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Position</p>
              <p className="text-3xl font-bold text-gray-900">#{avgPosition.toFixed(1)}</p>
            </div>
            <TrendingUp className="h-10 w-10 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Competitor Cards */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Top Competitors
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {competitors.map((competitor, index) => (
            <CompetitorCard
              key={competitor.domain}
              competitor={competitor}
              rank={index + 1}
            />
          ))}
        </div>
      </div>

      {/* Insights */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          Competitive Insights
        </h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            • Top competitor ({competitors[0]?.domain}) appears in{' '}
            <strong>{competitors[0]?.appearances}</strong> SERPs with an average position of{' '}
            <strong>#{competitors[0]?.avg_position.toFixed(1)}</strong>
          </p>
          <p>
            • Combined estimated traffic for top competitors:{' '}
            <strong>{(totalTraffic / 1000).toFixed(1)}K visits/month</strong>
          </p>
          <p>
            • Focus on content gaps where competitors are weak to gain market share
          </p>
        </div>
      </div>
    </div>
  );
}
