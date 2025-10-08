"use client";

import { KeywordCluster } from '@/types/cluster';
import { ChevronDown, ChevronUp, TrendingUp, Target, DollarSign } from 'lucide-react';
import { useState } from 'react';

interface ClusterCardProps {
  cluster: KeywordCluster;
  color: string;
}

export function ClusterCard({ cluster, color }: ClusterCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      className="bg-white rounded-lg border-2 hover:shadow-lg transition-all overflow-hidden"
      style={{ borderColor: color }}
    >
      {/* Header */}
      <div
        className="p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ backgroundColor: `${color}15` }}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-bold text-gray-900 mb-1">
              {cluster.cluster_name}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              {cluster.theme.description}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              <span className="text-xs px-2 py-1 bg-white rounded-full border font-medium">
                {cluster.total_keywords} keywords
              </span>
              <span className="text-xs px-2 py-1 bg-white rounded-full border font-medium">
                {cluster.primary_intent}
              </span>
            </div>
          </div>

          <button className="ml-4 p-2 hover:bg-white rounded-lg transition-colors">
            {isExpanded ? (
              <ChevronUp className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            )}
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-2 px-4 py-3 bg-gray-50 border-t border-gray-200">
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <TrendingUp className="h-3 w-3 text-blue-600" />
            <span className="text-xs text-gray-600">Volume</span>
          </div>
          <div className="text-sm font-bold text-gray-900">
            {cluster.total_search_volume.toLocaleString()}
          </div>
        </div>

        <div className="text-center border-x border-gray-300">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Target className="h-3 w-3 text-orange-600" />
            <span className="text-xs text-gray-600">Difficulty</span>
          </div>
          <div className="text-sm font-bold text-gray-900">
            {Math.round(cluster.avg_difficulty)}
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <DollarSign className="h-3 w-3 text-green-600" />
            <span className="text-xs text-gray-600">Avg CPC</span>
          </div>
          <div className="text-sm font-bold text-gray-900">
            ${cluster.avg_cpc.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="p-4 border-t border-gray-200 space-y-4">
          {/* Key Terms */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Terms</h4>
            <div className="flex flex-wrap gap-2">
              {cluster.theme.key_terms.map((term) => (
                <span
                  key={term}
                  className="px-2 py-1 text-sm bg-blue-50 text-blue-700 rounded-md border border-blue-200"
                >
                  {term}
                </span>
              ))}
            </div>
          </div>

          {/* SERP Features */}
          {cluster.common_serp_features.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Common SERP Features</h4>
              <div className="flex flex-wrap gap-2">
                {cluster.common_serp_features.map((feature) => (
                  <span
                    key={feature}
                    className="px-2 py-1 text-xs bg-purple-50 text-purple-700 rounded-md border border-purple-200"
                  >
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Keywords */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">
              All Keywords ({cluster.keywords.length})
            </h4>
            <div className="max-h-48 overflow-y-auto space-y-1">
              {cluster.keywords.map((keyword) => (
                <div
                  key={keyword}
                  className="text-sm text-gray-700 px-3 py-2 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
                >
                  {keyword}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
