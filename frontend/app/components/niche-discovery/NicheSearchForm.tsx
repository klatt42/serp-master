"use client";

import { useState } from 'react';
import { Search, Loader2, Sparkles } from 'lucide-react';

interface NicheSearchFormProps {
  onSearch: (seedKeyword: string, filters: any) => void;
  isLoading?: boolean;
}

export function NicheSearchForm({ onSearch, isLoading = false }: NicheSearchFormProps) {
  const [seedKeyword, setSeedKeyword] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Filters
  const [minVolume, setMinVolume] = useState(100);
  const [maxDifficulty, setMaxDifficulty] = useState(60);
  const [minCpc, setMinCpc] = useState<number | undefined>(undefined);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!seedKeyword.trim()) return;

    const filters = {
      min_volume: minVolume,
      max_difficulty: maxDifficulty,
      ...(minCpc && { min_cpc: minCpc }),
    };

    onSearch(seedKeyword, filters);
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Main Search Input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>

          <input
            type="text"
            value={seedKeyword}
            onChange={(e) => setSeedKeyword(e.target.value)}
            placeholder="Enter a seed keyword (e.g., 'local SEO', 'content marketing')"
            className="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
            disabled={isLoading}
          />

          {seedKeyword && (
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
              <Sparkles className="h-5 w-5 text-blue-500 animate-pulse" />
            </div>
          )}
        </div>

        {/* Advanced Filters Toggle */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {showAdvanced ? '← Hide' : '→ Show'} Advanced Filters
          </button>

          <button
            type="submit"
            disabled={isLoading || !seedKeyword.trim()}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="h-5 w-5" />
                Discover Niche
              </>
            )}
          </button>
        </div>

        {/* Advanced Filters Panel */}
        {showAdvanced && (
          <div className="bg-gray-50 rounded-lg p-6 space-y-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Filter Criteria</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Min Volume */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Min. Search Volume
                </label>
                <input
                  type="number"
                  value={minVolume}
                  onChange={(e) => setMinVolume(Number(e.target.value))}
                  min="0"
                  step="10"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Monthly searches minimum
                </p>
              </div>

              {/* Max Difficulty */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max. Difficulty
                </label>
                <input
                  type="number"
                  value={maxDifficulty}
                  onChange={(e) => setMaxDifficulty(Number(e.target.value))}
                  min="0"
                  max="100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  SEO difficulty (0-100)
                </p>
              </div>

              {/* Min CPC */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Min. CPC (Optional)
                </label>
                <input
                  type="number"
                  value={minCpc || ''}
                  onChange={(e) => setMinCpc(e.target.value ? Number(e.target.value) : undefined)}
                  min="0"
                  step="0.1"
                  placeholder="Any"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Cost per click in USD
                </p>
              </div>
            </div>

            {/* Preset Buttons */}
            <div className="flex flex-wrap gap-2 pt-2">
              <button
                type="button"
                onClick={() => {
                  setMinVolume(1000);
                  setMaxDifficulty(40);
                  setMinCpc(1.0);
                }}
                className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                🎯 Quick Wins
              </button>

              <button
                type="button"
                onClick={() => {
                  setMinVolume(100);
                  setMaxDifficulty(30);
                  setMinCpc(undefined);
                }}
                className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                🌱 Low Competition
              </button>

              <button
                type="button"
                onClick={() => {
                  setMinVolume(500);
                  setMaxDifficulty(70);
                  setMinCpc(2.0);
                }}
                className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                💰 High Value
              </button>
            </div>
          </div>
        )}
      </form>

      {/* Examples */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600 mb-2">Try these examples:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {['local SEO', 'content marketing', 'email automation', 'social media management'].map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => setSeedKeyword(example)}
              className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
