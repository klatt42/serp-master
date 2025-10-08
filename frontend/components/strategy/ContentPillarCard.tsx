/**
 * Content Pillar Card Component
 * Displays a single content pillar with keywords and metrics
 */

import React from 'react';
import { ContentPillar, Priority } from '@/types/strategy';
import { TrendingUp, Tag } from 'lucide-react';

interface ContentPillarCardProps {
  pillar: ContentPillar;
  itemCount: number;
}

const priorityColors = {
  [Priority.HIGH]: 'bg-red-100 text-red-800 border-red-300',
  [Priority.MEDIUM]: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  [Priority.LOW]: 'bg-green-100 text-green-800 border-green-300'
};

const priorityBorderColors = {
  [Priority.HIGH]: 'border-red-500',
  [Priority.MEDIUM]: 'border-yellow-500',
  [Priority.LOW]: 'border-green-500'
};

export default function ContentPillarCard({ pillar, itemCount }: ContentPillarCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md border-l-4 ${priorityBorderColors[pillar.priority]} p-6 hover:shadow-lg transition-shadow`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-gray-900">{pillar.name}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${priorityColors[pillar.priority]}`}>
          {pillar.priority.toUpperCase()}
        </span>
      </div>

      {/* Description */}
      <p className="text-gray-600 mb-4">{pillar.description}</p>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 rounded p-3">
          <p className="text-xs text-gray-500 mb-1">Total Opportunity</p>
          <p className="text-lg font-bold text-gray-900 flex items-center">
            <TrendingUp className="h-4 w-4 mr-1 text-green-500" />
            {pillar.total_opportunity.toLocaleString()}
          </p>
        </div>
        <div className="bg-gray-50 rounded p-3">
          <p className="text-xs text-gray-500 mb-1">Content Pieces</p>
          <p className="text-lg font-bold text-gray-900">{itemCount}</p>
        </div>
      </div>

      {/* Keywords */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
          <Tag className="h-4 w-4 mr-1" />
          Target Keywords
        </p>
        <div className="flex flex-wrap gap-2">
          {pillar.keywords.slice(0, 5).map((keyword, index) => (
            <span
              key={index}
              className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs border border-blue-200"
            >
              {keyword}
            </span>
          ))}
          {pillar.keywords.length > 5 && (
            <span className="text-xs text-gray-500 self-center">
              +{pillar.keywords.length - 5} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
