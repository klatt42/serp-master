/**
 * Strategy Overview Component
 * Displays high-level content strategy metrics and insights
 */

import React from 'react';
import { ContentStrategy } from '@/types/strategy';
import { TrendingUp, Calendar, Target, Zap } from 'lucide-react';

interface StrategyOverviewProps {
  strategy: ContentStrategy;
}

export default function StrategyOverview({ strategy }: StrategyOverviewProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-2">
          Content Strategy: {strategy.seed_keyword}
        </h2>
        <p className="text-purple-100">
          Generated on {new Date(strategy.generated_at).toLocaleDateString()}
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Content Pieces</p>
              <p className="text-3xl font-bold text-gray-900">{strategy.total_pieces}</p>
            </div>
            <Target className="h-10 w-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Content Pillars</p>
              <p className="text-3xl font-bold text-gray-900">{strategy.pillars.length}</p>
            </div>
            <TrendingUp className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Timeline</p>
              <p className="text-3xl font-bold text-gray-900">{strategy.timeline_weeks}w</p>
            </div>
            <Calendar className="h-10 w-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Est. Hours</p>
              <p className="text-3xl font-bold text-gray-900">{strategy.estimated_total_hours}</p>
            </div>
            <Zap className="h-10 w-10 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Quick Wins */}
      {strategy.quick_wins.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-3 flex items-center">
            <Zap className="h-5 w-5 mr-2" />
            Quick Wins
          </h3>
          <ul className="space-y-2">
            {strategy.quick_wins.map((win, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span className="text-green-800">{win}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Implementation Notes */}
      {strategy.implementation_notes && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            Implementation Notes
          </h3>
          <p className="text-blue-800">{strategy.implementation_notes}</p>
        </div>
      )}

      {/* Success Metrics */}
      {strategy.success_metrics.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Success Metrics to Track
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {strategy.success_metrics.map((metric, index) => (
              <div key={index} className="flex items-center space-x-2 bg-gray-50 p-3 rounded">
                <div className="h-2 w-2 bg-purple-500 rounded-full"></div>
                <span className="text-sm text-gray-700">{metric}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
