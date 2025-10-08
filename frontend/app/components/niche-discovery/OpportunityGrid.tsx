"use client";

import { KeywordOpportunity } from '@/types/opportunity';
import { OpportunityCard } from './OpportunityCard';
import { useState } from 'react';
import { Filter, ArrowUpDown } from 'lucide-react';

interface OpportunityGridProps {
  opportunities: KeywordOpportunity[];
}

type SortOption = 'score' | 'volume' | 'difficulty' | 'cpc';

export function OpportunityGrid({ opportunities }: OpportunityGridProps) {
  const [sortBy, setSortBy] = useState<SortOption>('score');
  const [filterLevel, setFilterLevel] = useState<string | null>(null);

  // Sort opportunities
  const sortedOpportunities = [...opportunities].sort((a, b) => {
    switch (sortBy) {
      case 'score':
        return b.opportunity_score - a.opportunity_score;
      case 'volume':
        return b.search_volume - a.search_volume;
      case 'difficulty':
        return a.keyword_difficulty - b.keyword_difficulty;
      case 'cpc':
        return b.cpc - a.cpc;
      default:
        return 0;
    }
  });

  // Filter opportunities
  const filteredOpportunities = filterLevel
    ? sortedOpportunities.filter(opp => opp.opportunity_level === filterLevel)
    : sortedOpportunities;

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Filter:</span>
          <div className="flex gap-2">
            {[
              { value: null, label: 'All' },
              { value: 'excellent', label: '🌟 Excellent' },
              { value: 'good', label: '👍 Good' },
              { value: 'moderate', label: '⚡ Moderate' },
            ].map((filter) => (
              <button
                key={filter.label}
                onClick={() => setFilterLevel(filter.value)}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  filterLevel === filter.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-5 w-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="score">Opportunity Score</option>
            <option value="volume">Search Volume</option>
            <option value="difficulty">Difficulty (Low→High)</option>
            <option value="cpc">CPC (High→Low)</option>
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Showing {filteredOpportunities.length} of {opportunities.length} opportunities
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredOpportunities.map((opportunity, index) => (
          <OpportunityCard
            key={opportunity.keyword}
            opportunity={opportunity}
            rank={filterLevel === null && sortBy === 'score' ? index + 1 : undefined}
          />
        ))}
      </div>

      {/* Empty State */}
      {filteredOpportunities.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No opportunities match your filters</p>
          <button
            onClick={() => setFilterLevel(null)}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
}
