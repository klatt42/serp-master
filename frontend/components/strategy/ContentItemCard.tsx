/**
 * Content Item Card Component
 * Displays individual content piece with details and status
 */

import React from 'react';
import { ContentItem, Priority, Difficulty, ContentStatus } from '@/types/strategy';
import { Calendar, Clock, Target, Lightbulb } from 'lucide-react';

interface ContentItemCardProps {
  item: ContentItem;
  onStatusChange?: (itemId: string, newStatus: ContentStatus) => void;
}

const priorityColors = {
  [Priority.HIGH]: 'bg-red-100 text-red-800 border-red-300',
  [Priority.MEDIUM]: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  [Priority.LOW]: 'bg-green-100 text-green-800 border-green-300'
};

const difficultyColors = {
  [Difficulty.EASY]: 'bg-green-100 text-green-800',
  [Difficulty.MEDIUM]: 'bg-yellow-100 text-yellow-800',
  [Difficulty.HARD]: 'bg-red-100 text-red-800'
};

const statusColors = {
  [ContentStatus.PLANNED]: 'bg-gray-100 text-gray-800',
  [ContentStatus.IN_PROGRESS]: 'bg-blue-100 text-blue-800',
  [ContentStatus.DRAFT]: 'bg-purple-100 text-purple-800',
  [ContentStatus.REVIEW]: 'bg-orange-100 text-orange-800',
  [ContentStatus.PUBLISHED]: 'bg-green-100 text-green-800'
};

const contentTypeIcons: Record<string, string> = {
  blog_post: '📝',
  guide: '📚',
  video: '🎥',
  infographic: '📊',
  case_study: '📈',
  tool: '🔧',
  checklist: '✅',
  comparison: '⚖️'
};

export default function ContentItemCard({ item, onStatusChange }: ContentItemCardProps) {
  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-5 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-start space-x-2">
          <span className="text-2xl">{contentTypeIcons[item.content_type] || '📄'}</span>
          <div>
            <h4 className="font-semibold text-gray-900">{item.title}</h4>
            <p className="text-sm text-gray-500">{item.pillar_name}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-semibold ${statusColors[item.status]}`}>
          {item.status.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      {/* Target Keyword */}
      <div className="mb-3">
        <p className="text-sm text-gray-600 flex items-center">
          <Target className="h-4 w-4 mr-1 text-blue-500" />
          <span className="font-semibold text-blue-700">{item.target_keyword}</span>
        </p>
        {item.supporting_keywords.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {item.supporting_keywords.slice(0, 3).map((keyword, index) => (
              <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                {keyword}
              </span>
            ))}
            {item.supporting_keywords.length > 3 && (
              <span className="text-xs text-gray-400">+{item.supporting_keywords.length - 3}</span>
            )}
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="flex items-center text-sm text-gray-600">
          <Calendar className="h-4 w-4 mr-1" />
          <span>{new Date(item.scheduled_date).toLocaleDateString()}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <Clock className="h-4 w-4 mr-1" />
          <span>{item.estimated_hours}h</span>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-3">
        <span className={`px-2 py-1 rounded text-xs font-semibold ${priorityColors[item.priority]}`}>
          {item.priority}
        </span>
        <span className={`px-2 py-1 rounded text-xs font-semibold ${difficultyColors[item.estimated_difficulty]}`}>
          {item.estimated_difficulty}
        </span>
        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
          {item.content_type.replace('_', ' ')}
        </span>
      </div>

      {/* Optimization Tips */}
      {item.optimization_tips.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
          <p className="text-xs font-semibold text-yellow-900 mb-2 flex items-center">
            <Lightbulb className="h-3 w-3 mr-1" />
            Optimization Tips
          </p>
          <ul className="space-y-1">
            {item.optimization_tips.slice(0, 2).map((tip, index) => (
              <li key={index} className="text-xs text-yellow-800 flex items-start">
                <span className="mr-1">•</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
          {item.optimization_tips.length > 2 && (
            <p className="text-xs text-yellow-600 mt-1">
              +{item.optimization_tips.length - 2} more tips
            </p>
          )}
        </div>
      )}

      {/* Status Change Buttons */}
      {onStatusChange && (
        <div className="mt-4 pt-3 border-t border-gray-200">
          <select
            value={item.status}
            onChange={(e) => onStatusChange(item.id, e.target.value as ContentStatus)}
            className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={ContentStatus.PLANNED}>Planned</option>
            <option value={ContentStatus.IN_PROGRESS}>In Progress</option>
            <option value={ContentStatus.DRAFT}>Draft</option>
            <option value={ContentStatus.REVIEW}>Review</option>
            <option value={ContentStatus.PUBLISHED}>Published</option>
          </select>
        </div>
      )}
    </div>
  );
}
