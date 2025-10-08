"use client";

import { KeywordOpportunity } from '@/types/opportunity';
import { TrendingUp, DollarSign, Target, Zap, ExternalLink } from 'lucide-react';

interface OpportunityCardProps {
  opportunity: KeywordOpportunity;
  rank?: number;
}

export function OpportunityCard({ opportunity, rank }: OpportunityCardProps) {

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'excellent': return 'bg-green-100 text-green-800 border-green-300';
      case 'good': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'excellent': return '🌟 Excellent';
      case 'good': return '👍 Good';
      case 'moderate': return '⚡ Moderate';
      default: return '📊 Low';
    }
  };

  const getEffortBadge = (effort: string) => {
    switch (effort.toLowerCase()) {
      case 'low': return '🟢 Low Effort';
      case 'medium': return '🟡 Medium Effort';
      case 'high': return '🔴 High Effort';
      default: return effort;
    }
  };

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 hover:border-blue-400 hover:shadow-lg transition-all p-6 relative">
      {/* Rank Badge */}
      {rank && rank <= 3 && (
        <div className="absolute -top-3 -left-3 w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold shadow-lg">
          {rank}
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-2">
            {opportunity.keyword}
          </h3>

          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-xs px-2 py-1 rounded-full font-semibold border ${getLevelColor(opportunity.opportunity_level)}`}>
              {getLevelBadge(opportunity.opportunity_level)}
            </span>

            <span className="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-700 border border-purple-300 font-medium">
              {opportunity.recommended_content_type}
            </span>
          </div>
        </div>

        {/* Opportunity Score */}
        <div className="ml-4 text-center">
          <div className="text-3xl font-bold text-blue-600">
            {Math.round(opportunity.opportunity_score)}
          </div>
          <div className="text-xs text-gray-500 font-medium">Score</div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Search Volume */}
        <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="h-4 w-4 text-blue-600" />
            <span className="text-xs font-medium text-blue-900">Volume</span>
          </div>
          <div className="text-lg font-bold text-blue-700">
            {opportunity.search_volume.toLocaleString()}
            <span className="text-xs font-normal text-blue-600">/mo</span>
          </div>
        </div>

        {/* CPC */}
        <div className="bg-green-50 rounded-lg p-3 border border-green-200">
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="h-4 w-4 text-green-600" />
            <span className="text-xs font-medium text-green-900">CPC</span>
          </div>
          <div className="text-lg font-bold text-green-700">
            ${opportunity.cpc.toFixed(2)}
          </div>
        </div>

        {/* Difficulty */}
        <div className="bg-orange-50 rounded-lg p-3 border border-orange-200">
          <div className="flex items-center gap-2 mb-1">
            <Target className="h-4 w-4 text-orange-600" />
            <span className="text-xs font-medium text-orange-900">Difficulty</span>
          </div>
          <div className="text-lg font-bold text-orange-700">
            {opportunity.keyword_difficulty}/100
          </div>
        </div>

        {/* Est. Traffic */}
        <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="h-4 w-4 text-purple-600" />
            <span className="text-xs font-medium text-purple-900">Est. Traffic</span>
          </div>
          <div className="text-lg font-bold text-purple-700">
            {opportunity.estimated_traffic.toLocaleString()}
            <span className="text-xs font-normal text-purple-600">/mo</span>
          </div>
        </div>
      </div>

      {/* ROI & Effort */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-200">
        <div>
          <div className="text-xs text-gray-500 mb-1">ROI Potential</div>
          <div className="text-sm font-bold text-gray-900">
            {opportunity.roi_potential.toFixed(1)}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500 mb-1">Effort Level</div>
          <div className="text-sm font-medium">
            {getEffortBadge(opportunity.effort_level)}
          </div>
        </div>
      </div>

      {/* Action Button */}
      <button className="mt-4 w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2">
        <ExternalLink className="h-4 w-4" />
        Create Content Strategy
      </button>
    </div>
  );
}
