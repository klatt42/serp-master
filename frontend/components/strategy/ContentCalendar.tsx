/**
 * Content Calendar Component
 * Displays content items in a weekly timeline view
 */

import React, { useMemo } from 'react';
import { ContentItem, ContentStatus } from '@/types/strategy';
import ContentItemCard from './ContentItemCard';
import { ChevronLeft, ChevronRight, Download } from 'lucide-react';

interface ContentCalendarProps {
  items: ContentItem[];
  onStatusChange?: (itemId: string, newStatus: ContentStatus) => void;
  onExport?: (format: 'ics' | 'csv') => void;
}

interface WeekGroup {
  weekNumber: number;
  startDate: Date;
  endDate: Date;
  items: ContentItem[];
}

export default function ContentCalendar({ items, onStatusChange, onExport }: ContentCalendarProps) {
  const [currentWeekIndex, setCurrentWeekIndex] = React.useState(0);

  // Group items by week
  const weekGroups = useMemo((): WeekGroup[] => {
    if (items.length === 0) return [];

    // Sort items by date
    const sortedItems = [...items].sort((a, b) =>
      new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime()
    );

    const baseDate = new Date(sortedItems[0].scheduled_date);
    const weeks = new Map<number, ContentItem[]>();

    sortedItems.forEach(item => {
      const itemDate = new Date(item.scheduled_date);
      const weekNumber = Math.floor((itemDate.getTime() - baseDate.getTime()) / (7 * 24 * 60 * 60 * 1000)) + 1;

      if (!weeks.has(weekNumber)) {
        weeks.set(weekNumber, []);
      }
      weeks.get(weekNumber)!.push(item);
    });

    return Array.from(weeks.entries()).map(([weekNumber, weekItems]) => {
      const weekStartDate = new Date(baseDate.getTime() + (weekNumber - 1) * 7 * 24 * 60 * 60 * 1000);
      const weekEndDate = new Date(weekStartDate.getTime() + 6 * 24 * 60 * 60 * 1000);

      return {
        weekNumber,
        startDate: weekStartDate,
        endDate: weekEndDate,
        items: weekItems
      };
    }).sort((a, b) => a.weekNumber - b.weekNumber);
  }, [items]);

  const currentWeek = weekGroups[currentWeekIndex];

  const goToPreviousWeek = () => {
    setCurrentWeekIndex(prev => Math.max(0, prev - 1));
  };

  const goToNextWeek = () => {
    setCurrentWeekIndex(prev => Math.min(weekGroups.length - 1, prev + 1));
  };

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p className="text-gray-500">No content items scheduled yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Calendar Header */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-gray-900">Content Calendar</h3>
          {onExport && (
            <div className="flex space-x-2">
              <button
                onClick={() => onExport('ics')}
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                <Download className="h-4 w-4 mr-1" />
                Export ICS
              </button>
              <button
                onClick={() => onExport('csv')}
                className="flex items-center px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
              >
                <Download className="h-4 w-4 mr-1" />
                Export CSV
              </button>
            </div>
          )}
        </div>

        {/* Week Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={goToPreviousWeek}
            disabled={currentWeekIndex === 0}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>

          <div className="text-center">
            <p className="text-lg font-semibold text-gray-900">
              Week {currentWeek?.weekNumber} of {weekGroups.length}
            </p>
            <p className="text-sm text-gray-600">
              {currentWeek?.startDate.toLocaleDateString()} - {currentWeek?.endDate.toLocaleDateString()}
            </p>
          </div>

          <button
            onClick={goToNextWeek}
            disabled={currentWeekIndex === weekGroups.length - 1}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        {/* Week Overview */}
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-blue-50 rounded p-3">
            <p className="text-xs text-blue-600 mb-1">Total Items</p>
            <p className="text-2xl font-bold text-blue-900">{currentWeek?.items.length || 0}</p>
          </div>
          <div className="bg-green-50 rounded p-3">
            <p className="text-xs text-green-600 mb-1">Planned</p>
            <p className="text-2xl font-bold text-green-900">
              {currentWeek?.items.filter(i => i.status === ContentStatus.PLANNED).length || 0}
            </p>
          </div>
          <div className="bg-purple-50 rounded p-3">
            <p className="text-xs text-purple-600 mb-1">In Progress</p>
            <p className="text-2xl font-bold text-purple-900">
              {currentWeek?.items.filter(i => i.status === ContentStatus.IN_PROGRESS).length || 0}
            </p>
          </div>
          <div className="bg-orange-50 rounded p-3">
            <p className="text-xs text-orange-600 mb-1">Est. Hours</p>
            <p className="text-2xl font-bold text-orange-900">
              {currentWeek?.items.reduce((sum, item) => sum + item.estimated_hours, 0) || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Content Items for Current Week */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {currentWeek?.items.map(item => (
          <ContentItemCard
            key={item.id}
            item={item}
            onStatusChange={onStatusChange}
          />
        ))}
      </div>

      {/* Weekly Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-2">Quick Week Overview</h4>
        <div className="grid grid-cols-1 md:grid-cols-7 gap-2">
          {weekGroups.map((week, index) => (
            <button
              key={week.weekNumber}
              onClick={() => setCurrentWeekIndex(index)}
              className={`p-2 rounded text-center transition-colors ${
                index === currentWeekIndex
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <p className="text-xs font-semibold">W{week.weekNumber}</p>
              <p className="text-xs">{week.items.length}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
