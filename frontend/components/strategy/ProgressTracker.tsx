/**
 * Progress Tracker Component
 * Visualizes content strategy execution progress
 */

import React, { useMemo } from 'react';
import { ContentStrategy, ContentStatus, Priority } from '@/types/strategy';
import { CheckCircle, Circle, Clock, TrendingUp, Target } from 'lucide-react';

interface ProgressTrackerProps {
  strategy: ContentStrategy;
}

export default function ProgressTracker({ strategy }: ProgressTrackerProps) {
  const stats = useMemo(() => {
    const total = strategy.content_items.length;
    const byStatus = {
      planned: strategy.content_items.filter(i => i.status === ContentStatus.PLANNED).length,
      inProgress: strategy.content_items.filter(i => i.status === ContentStatus.IN_PROGRESS).length,
      draft: strategy.content_items.filter(i => i.status === ContentStatus.DRAFT).length,
      review: strategy.content_items.filter(i => i.status === ContentStatus.REVIEW).length,
      published: strategy.content_items.filter(i => i.status === ContentStatus.PUBLISHED).length
    };

    const byPriority = {
      high: strategy.content_items.filter(i => i.priority === Priority.HIGH).length,
      medium: strategy.content_items.filter(i => i.priority === Priority.MEDIUM).length,
      low: strategy.content_items.filter(i => i.priority === Priority.LOW).length
    };

    const completed = byStatus.published;
    const inProgress = byStatus.inProgress + byStatus.draft + byStatus.review;
    const completionRate = total > 0 ? (completed / total) * 100 : 0;

    const hoursCompleted = strategy.content_items
      .filter(i => i.status === ContentStatus.PUBLISHED)
      .reduce((sum, i) => sum + i.estimated_hours, 0);

    const hoursRemaining = strategy.estimated_total_hours - hoursCompleted;

    return {
      total,
      byStatus,
      byPriority,
      completed,
      inProgress,
      completionRate,
      hoursCompleted,
      hoursRemaining
    };
  }, [strategy]);

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="h-6 w-6 mr-2 text-blue-600" />
          Overall Progress
        </h3>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Completion</span>
            <span className="font-semibold">{stats.completionRate.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-green-500 h-full transition-all duration-500"
              style={{ width: `${stats.completionRate}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{stats.completed} published</span>
            <span>{stats.total - stats.completed} remaining</span>
          </div>
        </div>

        {/* Status Breakdown */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="bg-gray-50 rounded p-3 text-center">
            <Circle className="h-5 w-5 text-gray-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-gray-900">{stats.byStatus.planned}</p>
            <p className="text-xs text-gray-600">Planned</p>
          </div>
          <div className="bg-blue-50 rounded p-3 text-center">
            <Clock className="h-5 w-5 text-blue-600 mx-auto mb-1" />
            <p className="text-2xl font-bold text-blue-900">{stats.byStatus.inProgress}</p>
            <p className="text-xs text-blue-600">In Progress</p>
          </div>
          <div className="bg-purple-50 rounded p-3 text-center">
            <Circle className="h-5 w-5 text-purple-600 mx-auto mb-1" />
            <p className="text-2xl font-bold text-purple-900">{stats.byStatus.draft}</p>
            <p className="text-xs text-purple-600">Draft</p>
          </div>
          <div className="bg-orange-50 rounded p-3 text-center">
            <Circle className="h-5 w-5 text-orange-600 mx-auto mb-1" />
            <p className="text-2xl font-bold text-orange-900">{stats.byStatus.review}</p>
            <p className="text-xs text-orange-600">Review</p>
          </div>
          <div className="bg-green-50 rounded p-3 text-center">
            <CheckCircle className="h-5 w-5 text-green-600 mx-auto mb-1" />
            <p className="text-2xl font-bold text-green-900">{stats.byStatus.published}</p>
            <p className="text-xs text-green-600">Published</p>
          </div>
        </div>
      </div>

      {/* Priority Distribution */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Target className="h-5 w-5 mr-2 text-purple-600" />
          Priority Distribution
        </h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-red-700 font-semibold">High Priority</span>
              <span className="text-gray-600">{stats.byPriority.high} items</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-red-500 h-full rounded-full"
                style={{ width: `${(stats.byPriority.high / stats.total) * 100}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-yellow-700 font-semibold">Medium Priority</span>
              <span className="text-gray-600">{stats.byPriority.medium} items</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-yellow-500 h-full rounded-full"
                style={{ width: `${(stats.byPriority.medium / stats.total) * 100}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-green-700 font-semibold">Low Priority</span>
              <span className="text-gray-600">{stats.byPriority.low} items</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-full rounded-full"
                style={{ width: `${(stats.byPriority.low / stats.total) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Time Tracking */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Clock className="h-5 w-5 mr-2 text-orange-600" />
          Time Investment
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded p-4 text-center">
            <p className="text-sm text-blue-600 mb-1">Total Estimated</p>
            <p className="text-3xl font-bold text-blue-900">{strategy.estimated_total_hours}h</p>
          </div>
          <div className="bg-green-50 rounded p-4 text-center">
            <p className="text-sm text-green-600 mb-1">Completed</p>
            <p className="text-3xl font-bold text-green-900">{stats.hoursCompleted}h</p>
          </div>
          <div className="bg-orange-50 rounded p-4 text-center">
            <p className="text-sm text-orange-600 mb-1">Remaining</p>
            <p className="text-3xl font-bold text-orange-900">{stats.hoursRemaining}h</p>
          </div>
        </div>

        {/* Time Progress Bar */}
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-green-500 to-blue-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${(stats.hoursCompleted / strategy.estimated_total_hours) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Pillar Progress */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Progress by Content Pillar
        </h3>
        <div className="space-y-4">
          {strategy.pillars.map(pillar => {
            const pillarItems = strategy.content_items.filter(i => i.pillar_name === pillar.name);
            const pillarCompleted = pillarItems.filter(i => i.status === ContentStatus.PUBLISHED).length;
            const pillarProgress = pillarItems.length > 0 ? (pillarCompleted / pillarItems.length) * 100 : 0;

            return (
              <div key={pillar.id}>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-semibold text-gray-900">{pillar.name}</span>
                  <span className="text-gray-600">
                    {pillarCompleted}/{pillarItems.length} published
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${pillarProgress}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Next Actions */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-purple-900 mb-3">
          Recommended Next Actions
        </h3>
        <ul className="space-y-2">
          {stats.byStatus.planned > 0 && (
            <li className="flex items-start text-sm text-purple-800">
              <span className="text-purple-600 mr-2">→</span>
              <span>Start working on {stats.byStatus.planned} planned items</span>
            </li>
          )}
          {stats.byStatus.draft > 0 && (
            <li className="flex items-start text-sm text-purple-800">
              <span className="text-purple-600 mr-2">→</span>
              <span>Move {stats.byStatus.draft} drafts to review</span>
            </li>
          )}
          {stats.byStatus.review > 0 && (
            <li className="flex items-start text-sm text-purple-800">
              <span className="text-purple-600 mr-2">→</span>
              <span>Publish {stats.byStatus.review} items in review</span>
            </li>
          )}
          {stats.byPriority.high > stats.completed && (
            <li className="flex items-start text-sm text-purple-800">
              <span className="text-purple-600 mr-2">→</span>
              <span>Focus on {stats.byPriority.high} high-priority items</span>
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
