/**
 * Content Strategy Page
 * Week 8: AI-Powered Content Strategy Generation
 */

'use client';

import React, { useState } from 'react';
import { CopilotKit } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import {
  ContentStrategy,
  StrategyGenerationRequest,
  Competitor,
  CompetitiveAnalysisRequest,
  ContentStatus,
  ContentType
} from '@/types/strategy';
import StrategyOverview from '@/components/strategy/StrategyOverview';
import ContentPillarCard from '@/components/strategy/ContentPillarCard';
import ContentCalendar from '@/components/strategy/ContentCalendar';
import CompetitorAnalysis from '@/components/strategy/CompetitorAnalysis';
import ProgressTracker from '@/components/strategy/ProgressTracker';
import StrategyAssistant from '@/components/strategy/StrategyAssistant';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sparkles, TrendingUp, Calendar as CalendarIcon, Users, BarChart, MessageSquare } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function StrategyPage() {
  const [strategy, setStrategy] = useState<ContentStrategy | null>(null);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [seedKeyword, setSeedKeyword] = useState('');
  const [timelineWeeks, setTimelineWeeks] = useState(12);
  const [contentTypes, setContentTypes] = useState<ContentType[]>([
    ContentType.BLOG_POST,
    ContentType.GUIDE,
    ContentType.VIDEO
  ]);

  const generateStrategy = async () => {
    if (!seedKeyword.trim()) {
      setError('Please enter a seed keyword');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request: StrategyGenerationRequest = {
        seed_keyword: seedKeyword,
        timeline_weeks: timelineWeeks,
        content_types: contentTypes,
        max_pieces_per_week: 3
      };

      const response = await fetch(`${API_URL}/api/strategy/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate strategy');
      }

      const data = await response.json();
      setStrategy(data);

      // Also analyze competitors
      await analyzeCompetitors(data.pillars.flatMap((p: any) => p.keywords.slice(0, 2)));
    } catch (err: any) {
      setError(err.message);
      console.error('Strategy generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const analyzeCompetitors = async (keywords: string[]) => {
    if (keywords.length === 0) return;

    setIsAnalyzing(true);
    try {
      const request: CompetitiveAnalysisRequest = {
        keywords: keywords.slice(0, 10),
        max_competitors: 10
      };

      const response = await fetch(`${API_URL}/api/strategy/competitors/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });

      if (response.ok) {
        const data = await response.json();
        setCompetitors(data);
      }
    } catch (err) {
      console.error('Competitor analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleStatusChange = (itemId: string, newStatus: ContentStatus) => {
    if (!strategy) return;

    const updatedItems = strategy.content_items.map(item =>
      item.id === itemId ? { ...item, status: newStatus } : item
    );

    setStrategy({
      ...strategy,
      content_items: updatedItems
    });
  };

  const handleExport = async (format: 'ics' | 'csv') => {
    if (!strategy) return;

    try {
      const response = await fetch(
        `${API_URL}/api/strategy/calendar/export-${format}?strategy_id=current`,
        { method: 'POST' }
      );

      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([data.content], {
          type: format === 'ics' ? 'text/calendar' : 'text/csv'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `content-strategy.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Export error:', err);
    }
  };

  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center">
              <Sparkles className="h-8 w-8 mr-3 text-purple-600" />
              AI Content Strategy Generator
            </h1>
            <p className="text-gray-600">
              Generate comprehensive SEO content strategies powered by GPT-4
            </p>
          </div>

          {/* Generation Form */}
          {!strategy && (
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Generate Your Strategy
              </h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seed Keyword / Niche
                  </label>
                  <input
                    type="text"
                    value={seedKeyword}
                    onChange={(e) => setSeedKeyword(e.target.value)}
                    placeholder="e.g., digital marketing, vegan recipes, remote work"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timeline (weeks)
                    </label>
                    <input
                      type="number"
                      value={timelineWeeks}
                      onChange={(e) => setTimelineWeeks(parseInt(e.target.value) || 12)}
                      min="4"
                      max="52"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Content Types
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {[ContentType.BLOG_POST, ContentType.GUIDE, ContentType.VIDEO, ContentType.INFOGRAPHIC].map(type => (
                        <button
                          key={type}
                          onClick={() => {
                            setContentTypes(prev =>
                              prev.includes(type)
                                ? prev.filter(t => t !== type)
                                : [...prev, type]
                            );
                          }}
                          className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                            contentTypes.includes(type)
                              ? 'bg-purple-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {type.replace('_', ' ')}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

                <button
                  onClick={generateStrategy}
                  disabled={isGenerating}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-4 rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Generating Strategy...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5 mr-2" />
                      Generate AI Strategy
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Strategy Display */}
          {strategy && (
            <div className="space-y-8">
              {/* Quick Actions */}
              <div className="bg-white rounded-lg shadow p-4">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-gray-900">
                    Strategy for: {strategy.seed_keyword}
                  </h3>
                  <button
                    onClick={() => {
                      setStrategy(null);
                      setCompetitors([]);
                      setSeedKeyword('');
                    }}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                  >
                    Generate New Strategy
                  </button>
                </div>
              </div>

              {/* Tabs */}
              <Tabs defaultValue="overview" className="w-full">
                <TabsList className="bg-white p-1 rounded-lg shadow mb-6">
                  <TabsTrigger value="overview" className="flex items-center">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Overview
                  </TabsTrigger>
                  <TabsTrigger value="pillars" className="flex items-center">
                    <BarChart className="h-4 w-4 mr-2" />
                    Pillars
                  </TabsTrigger>
                  <TabsTrigger value="calendar" className="flex items-center">
                    <CalendarIcon className="h-4 w-4 mr-2" />
                    Calendar
                  </TabsTrigger>
                  <TabsTrigger value="competitors" className="flex items-center">
                    <Users className="h-4 w-4 mr-2" />
                    Competitors
                  </TabsTrigger>
                  <TabsTrigger value="progress" className="flex items-center">
                    <BarChart className="h-4 w-4 mr-2" />
                    Progress
                  </TabsTrigger>
                  <TabsTrigger value="assistant" className="flex items-center">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    AI Assistant
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="overview">
                  <StrategyOverview strategy={strategy} />
                </TabsContent>

                <TabsContent value="pillars">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {strategy.pillars.map(pillar => {
                      const itemCount = strategy.content_items.filter(
                        i => i.pillar_name === pillar.name
                      ).length;
                      return (
                        <ContentPillarCard
                          key={pillar.id}
                          pillar={pillar}
                          itemCount={itemCount}
                        />
                      );
                    })}
                  </div>
                </TabsContent>

                <TabsContent value="calendar">
                  <ContentCalendar
                    items={strategy.content_items}
                    onStatusChange={handleStatusChange}
                    onExport={handleExport}
                  />
                </TabsContent>

                <TabsContent value="competitors">
                  <CompetitorAnalysis
                    competitors={competitors}
                    isLoading={isAnalyzing}
                  />
                </TabsContent>

                <TabsContent value="progress">
                  <ProgressTracker strategy={strategy} />
                </TabsContent>

                <TabsContent value="assistant">
                  <div className="bg-white rounded-lg shadow" style={{ height: '600px' }}>
                    <StrategyAssistant strategy={strategy} />
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </div>
      </div>
    </CopilotKit>
  );
}
