"use client";

import { ContentGap } from '@/types/niche';
import { AlertTriangle, TrendingUp, Zap, Target } from 'lucide-react';

interface ContentGapListProps {
  gaps: ContentGap[];
}

export function ContentGapList({ gaps }: ContentGapListProps) {

  const getImpactIcon = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high': return <TrendingUp className="h-5 w-5 text-red-600" />;
      case 'medium': return <Zap className="h-5 w-5 text-yellow-600" />;
      default: return <Target className="h-5 w-5 text-blue-600" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high': return 'border-red-300 bg-red-50';
      case 'medium': return 'border-yellow-300 bg-yellow-50';
      default: return 'border-blue-300 bg-blue-50';
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="h-6 w-6 text-orange-600" />
        <h2 className="text-2xl font-bold text-gray-900">Content Gaps & Opportunities</h2>
      </div>

      <p className="text-gray-600 mb-6">
        Identified opportunities where you can create content to capture traffic.
      </p>

      <div className="space-y-4">
        {gaps.map((gap, index) => (
          <div
            key={index}
            className={`rounded-lg border-2 p-6 ${getImpactColor(gap.estimated_impact)}`}
          >
            <div className="flex items-start gap-4">
              {/* Icon */}
              <div className="p-3 bg-white rounded-lg shadow-sm">
                {getImpactIcon(gap.estimated_impact)}
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-bold text-gray-900">
                    {gap.gap_type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                  </h3>

                  <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${getPriorityBadge(gap.priority)}`}>
                    {gap.priority.toUpperCase()} Priority
                  </span>
                </div>

                <p className="text-gray-700 mb-4">
                  {gap.description}
                </p>

                {/* Keywords */}
                <div>
                  <div className="text-sm font-semibold text-gray-700 mb-2">Example Keywords:</div>
                  <div className="flex flex-wrap gap-2">
                    {gap.keywords.map((keyword) => (
                      <span
                        key={keyword}
                        className="px-3 py-1 text-sm bg-white text-gray-800 rounded-md border border-gray-300 font-medium"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {gaps.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <p className="text-gray-500">No content gaps identified yet.</p>
          <p className="text-sm text-gray-400 mt-2">Run a niche analysis to discover opportunities.</p>
        </div>
      )}
    </div>
  );
}
