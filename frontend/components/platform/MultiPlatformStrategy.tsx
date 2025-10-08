"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import PlatformSelector from './PlatformSelector';
import IntentMatrix from './IntentMatrix';

interface UnifiedStrategy {
  priority_platform: string;
  platform_breakdown: Record<string, number>;
  dominant_intent: string;
  intent_distribution: Record<string, number>;
  immediate_actions: string[];
  cross_platform_workflow: Array<{
    step: number;
    action: string;
    goal: string;
  }>;
}

interface StrategyResponse {
  success: boolean;
  data: {
    platform_analysis: any;
    intent_analysis: any;
    unified_strategy: UnifiedStrategy;
  };
  summary: {
    platforms_covered: number;
    content_opportunities: number;
    cross_platform_ideas: number;
    recommended_focus: string;
  };
}

export default function MultiPlatformStrategy() {
  const [keywords, setKeywords] = useState<string>('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([
    'youtube',
    'tiktok',
    'amazon',
    'reddit'
  ]);
  const [loading, setLoading] = useState(false);
  const [strategy, setStrategy] = useState<StrategyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateStrategy = async () => {
    if (!keywords.trim()) {
      setError('Please enter at least one keyword');
      return;
    }

    if (selectedPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const keywordList = keywords
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);

      const response = await fetch('http://localhost:8000/api/platform/strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          niche_keywords: keywordList,
          target_platforms: selectedPlatforms,
          location: 'United States'
        }),
      });

      const data = await response.json();

      if (data.success) {
        setStrategy(data);
      } else {
        setError('Failed to generate strategy');
      }
    } catch (err) {
      setError('Error generating strategy. Please check your connection.');
      console.error('Strategy generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Multi-Platform Content Strategy</CardTitle>
          <CardDescription>
            Generate a unified content strategy across multiple platforms based on keyword intent analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Keywords (comma-separated)
            </label>
            <Input
              placeholder="e.g., keto recipes, weight loss tips, healthy eating"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              disabled={loading}
            />
          </div>

          <PlatformSelector
            selectedPlatforms={selectedPlatforms}
            onPlatformChange={setSelectedPlatforms}
          />

          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          <Button
            onClick={handleGenerateStrategy}
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Generating Strategy...' : 'Generate Multi-Platform Strategy'}
          </Button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {strategy && (
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="intent">Intent Analysis</TabsTrigger>
            <TabsTrigger value="platforms">Platform Breakdown</TabsTrigger>
            <TabsTrigger value="workflow">Action Plan</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Strategy Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Platforms Analyzed</p>
                    <p className="text-3xl font-bold">{strategy.summary.platforms_covered}</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Content Opportunities</p>
                    <p className="text-3xl font-bold">{strategy.summary.content_opportunities}</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Cross-Platform Ideas</p>
                    <p className="text-3xl font-bold">{strategy.summary.cross_platform_ideas}</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Priority Platform</p>
                    <p className="text-2xl font-bold capitalize">{strategy.data.unified_strategy.priority_platform}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Immediate Actions</CardTitle>
                <CardDescription>Quick wins to get started</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {strategy.data.unified_strategy.immediate_actions.map((action, index) => (
                    <li key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm">
                        {index + 1}
                      </span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Intent Analysis Tab */}
          <TabsContent value="intent">
            <IntentMatrix
              intentDistribution={strategy.data.intent_analysis.insights.intent_distribution}
              classifications={strategy.data.intent_analysis.classifications}
              topPlatforms={strategy.data.intent_analysis.insights.top_platforms}
            />
          </TabsContent>

          {/* Platform Breakdown Tab */}
          <TabsContent value="platforms" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Platform Opportunities</CardTitle>
                <CardDescription>
                  Content opportunities discovered per platform
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(strategy.data.unified_strategy.platform_breakdown)
                    .sort(([, a], [, b]) => (b as number) - (a as number))
                    .map(([platform, count]) => (
                      <div key={platform} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">
                            {platform === 'youtube' && '🎥'}
                            {platform === 'tiktok' && '📱'}
                            {platform === 'amazon' && '🛒'}
                            {platform === 'reddit' && '💬'}
                            {platform === 'google' && '🔍'}
                            {platform === 'blog' && '📝'}
                          </span>
                          <div>
                            <h4 className="font-semibold capitalize">{platform}</h4>
                            <p className="text-sm text-gray-500">
                              {count} content opportunities
                            </p>
                          </div>
                        </div>
                        <Badge variant="secondary">{count}</Badge>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            {strategy.data.platform_analysis.cross_platform_opportunities.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Cross-Platform Opportunities</CardTitle>
                  <CardDescription>
                    Keywords that work across multiple platforms
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {strategy.data.platform_analysis.cross_platform_opportunities.map((opp: any, index: number) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold">{opp.keyword}</h4>
                          <Badge>{opp.platform_count} platforms</Badge>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {opp.platforms.map((platform: string) => (
                            <Badge key={platform} variant="outline" className="capitalize">
                              {platform}
                            </Badge>
                          ))}
                        </div>
                        <p className="text-sm text-gray-500 mt-2">{opp.recommendation}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Workflow Tab */}
          <TabsContent value="workflow">
            <Card>
              <CardHeader>
                <CardTitle>Cross-Platform Content Workflow</CardTitle>
                <CardDescription>
                  Step-by-step strategy to build your content funnel
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {strategy.data.unified_strategy.cross_platform_workflow.map((step) => (
                    <div key={step.step} className="flex gap-4 p-4 border rounded-lg">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">
                        {step.step}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-lg mb-1">{step.action}</h4>
                        <p className="text-gray-600 dark:text-gray-400">
                          <span className="font-medium">Goal:</span> {step.goal}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
