/**
 * Competitor Card Component
 * Displays competitor analysis with strengths and weaknesses
 */

import React from 'react';
import { Competitor } from '@/types/strategy';
import { TrendingUp, TrendingDown, Globe, Target, BarChart } from 'lucide-react';

interface CompetitorCardProps {
  competitor: Competitor;
  rank: number;
}

export default function CompetitorCard({ competitor, rank }: CompetitorCardProps) {
  const getRankColor = (rank: number) => {
    if (rank === 1) return 'bg-yellow-100 border-yellow-400 text-yellow-900';
    if (rank === 2) return 'bg-gray-100 border-gray-400 text-gray-900';
    if (rank === 3) return 'bg-orange-100 border-orange-400 text-orange-900';
    return 'bg-blue-100 border-blue-400 text-blue-900';
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-12 h-12 rounded-full border-2 ${getRankColor(rank)} flex items-center justify-center text-xl font-bold`}>
            {getRankBadge(rank)}
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <Globe className="h-4 w-4 mr-1 text-blue-500" />
              {competitor.domain}
            </h3>
            <p className="text-sm text-gray-500">{competitor.appearances} SERP appearances</p>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-blue-50 rounded p-3">
          <p className="text-xs text-blue-600 mb-1">Avg Position</p>
          <p className="text-xl font-bold text-blue-900">#{competitor.avg_position.toFixed(1)}</p>
        </div>
        <div className="bg-green-50 rounded p-3">
          <p className="text-xs text-green-600 mb-1">Traffic Est.</p>
          <p className="text-xl font-bold text-green-900">
            {(competitor.estimated_traffic / 1000).toFixed(1)}K
          </p>
        </div>
        <div className="bg-purple-50 rounded p-3">
          <p className="text-xs text-purple-600 mb-1">Authority</p>
          <p className="text-xl font-bold text-purple-900">{competitor.domain_authority}</p>
        </div>
      </div>

      {/* Keywords Ranked */}
      <div className="mb-4">
        <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
          <Target className="h-4 w-4 mr-1" />
          Keywords Ranked ({competitor.keywords_ranked.length})
        </p>
        <div className="flex flex-wrap gap-1">
          {competitor.keywords_ranked.slice(0, 4).map((keyword, index) => (
            <span
              key={index}
              className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
            >
              {keyword}
            </span>
          ))}
          {competitor.keywords_ranked.length > 4 && (
            <span className="text-xs text-gray-500 self-center">
              +{competitor.keywords_ranked.length - 4} more
            </span>
          )}
        </div>
      </div>

      {/* Content Types */}
      {competitor.content_types.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
            <BarChart className="h-4 w-4 mr-1" />
            Content Types
          </p>
          <div className="flex flex-wrap gap-2">
            {competitor.content_types.map((type, index) => (
              <span
                key={index}
                className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded border border-blue-200"
              >
                {type.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Strengths */}
      {competitor.strengths.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded p-3 mb-3">
          <p className="text-sm font-semibold text-green-900 mb-2 flex items-center">
            <TrendingUp className="h-4 w-4 mr-1" />
            Strengths
          </p>
          <ul className="space-y-1">
            {competitor.strengths.map((strength, index) => (
              <li key={index} className="text-xs text-green-800 flex items-start">
                <span className="text-green-600 mr-1">✓</span>
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weaknesses */}
      {competitor.weaknesses.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded p-3">
          <p className="text-sm font-semibold text-red-900 mb-2 flex items-center">
            <TrendingDown className="h-4 w-4 mr-1" />
            Opportunities (Their Weaknesses)
          </p>
          <ul className="space-y-1">
            {competitor.weaknesses.map((weakness, index) => (
              <li key={index} className="text-xs text-red-800 flex items-start">
                <span className="text-red-600 mr-1">→</span>
                <span>{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
