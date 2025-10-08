"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface IntentData {
  discovery: number;
  research: number;
  decision: number;
  validation: number;
}

interface Classification {
  keyword: string;
  primary_intent: string;
  confidence: number;
  recommended_platforms: Array<{
    platform: string;
    priority: string;
    intent_match: string;
  }>;
}

interface IntentMatrixProps {
  intentDistribution: IntentData;
  classifications: Classification[];
  topPlatforms?: Array<[string, { count: number; keywords: string[] }]>;
}

export default function IntentMatrix({
  intentDistribution,
  classifications,
  topPlatforms = []
}: IntentMatrixProps) {
  const getIntentColor = (intent: string) => {
    const colors: Record<string, string> = {
      discovery: 'bg-purple-500',
      research: 'bg-blue-500',
      decision: 'bg-green-500',
      validation: 'bg-orange-500'
    };
    return colors[intent.toLowerCase()] || 'bg-gray-500';
  };

  const getIntentIcon = (intent: string) => {
    const icons: Record<string, string> = {
      discovery: '🔍',
      research: '📚',
      decision: '✅',
      validation: '⭐'
    };
    return icons[intent.toLowerCase()] || '📊';
  };

  const getPriorityColor = (priority: string) => {
    if (priority === 'high') return 'text-green-600 dark:text-green-400';
    if (priority === 'medium') return 'text-yellow-600 dark:text-yellow-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  const totalKeywords = classifications.length;

  return (
    <div className="space-y-6">
      {/* Intent Distribution Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Intent Distribution</CardTitle>
          <CardDescription>
            How your {totalKeywords} keywords map to user intent stages
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(intentDistribution).map(([intent, percentage]) => (
              <div
                key={intent}
                className="p-4 border rounded-lg"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{getIntentIcon(intent)}</span>
                  <h3 className="font-semibold capitalize">{intent}</h3>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold">{percentage}%</span>
                  <span className="text-sm text-gray-500">of keywords</span>
                </div>
                <div className="mt-3 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getIntentColor(intent)}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Top Platforms */}
      {topPlatforms.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recommended Platforms</CardTitle>
            <CardDescription>
              Best platforms for your keyword set based on intent analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topPlatforms.slice(0, 5).map(([platform, data]) => (
                <div
                  key={platform}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">
                      {platform === 'youtube' && '🎥'}
                      {platform === 'tiktok' && '📱'}
                      {platform === 'amazon' && '🛒'}
                      {platform === 'reddit' && '💬'}
                      {platform === 'google' && '🔍'}
                      {platform === 'blog' && '📝'}
                      {!['youtube', 'tiktok', 'amazon', 'reddit', 'google', 'blog'].includes(platform) && '📊'}
                    </span>
                    <div>
                      <h4 className="font-semibold capitalize">{platform}</h4>
                      <p className="text-sm text-gray-500">
                        {data.count} keyword{data.count !== 1 ? 's' : ''} matched
                      </p>
                    </div>
                  </div>
                  <Badge variant="secondary">
                    {Math.round((data.count / totalKeywords) * 100)}%
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Keyword Classifications */}
      <Card>
        <CardHeader>
          <CardTitle>Keyword Intent Classifications</CardTitle>
          <CardDescription>
            Detailed intent analysis for each keyword
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {classifications.map((classification, index) => (
              <div
                key={index}
                className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-lg mb-1">
                      {classification.keyword}
                    </h4>
                    <div className="flex items-center gap-2">
                      <Badge className={`${getIntentColor(classification.primary_intent)} text-white`}>
                        {classification.primary_intent}
                      </Badge>
                      <span className="text-sm text-gray-500">
                        {Math.round(classification.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                </div>

                {classification.recommended_platforms.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      Recommended platforms:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {classification.recommended_platforms.map((rec, i) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className={getPriorityColor(rec.priority)}
                        >
                          {rec.platform} ({rec.priority})
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
