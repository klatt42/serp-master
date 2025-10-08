"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface Platform {
  id: string;
  name: string;
  intent: string;
  content_type: string;
}

interface PlatformSelectorProps {
  selectedPlatforms: string[];
  onPlatformChange: (platforms: string[]) => void;
}

export default function PlatformSelector({
  selectedPlatforms,
  onPlatformChange
}: PlatformSelectorProps) {
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/platform/platforms');
      const data = await response.json();

      if (data.success) {
        setPlatforms(data.platforms);
      }
    } catch (error) {
      console.error('Error fetching platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePlatform = (platformId: string) => {
    const newSelection = selectedPlatforms.includes(platformId)
      ? selectedPlatforms.filter(id => id !== platformId)
      : [...selectedPlatforms, platformId];

    onPlatformChange(newSelection);
  };

  const selectAll = () => {
    onPlatformChange(platforms.map(p => p.id));
  };

  const clearAll = () => {
    onPlatformChange([]);
  };

  const getPlatformIcon = (platformId: string) => {
    const icons: Record<string, string> = {
      youtube: '🎥',
      tiktok: '📱',
      amazon: '🛒',
      reddit: '💬',
      google: '🔍',
      blog: '📝'
    };
    return icons[platformId] || '📊';
  };

  const getIntentColor = (intent: string) => {
    const colors: Record<string, string> = {
      'Discovery': 'bg-purple-500',
      'Research': 'bg-blue-500',
      'Decision': 'bg-green-500',
      'Validation': 'bg-orange-500',
      'Research/Decision': 'bg-teal-500'
    };
    return colors[intent] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Platform Selection</CardTitle>
          <CardDescription>Loading platforms...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Platform Selection</CardTitle>
            <CardDescription>
              Select platforms to analyze ({selectedPlatforms.length} selected)
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={selectAll}
            >
              Select All
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={clearAll}
            >
              Clear
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {platforms.map((platform) => {
            const isSelected = selectedPlatforms.includes(platform.id);

            return (
              <div
                key={platform.id}
                onClick={() => togglePlatform(platform.id)}
                className={`
                  p-4 border rounded-lg cursor-pointer transition-all
                  ${isSelected
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                    : 'border-gray-200 hover:border-gray-300 dark:border-gray-700'
                  }
                `}
              >
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-3xl">{getPlatformIcon(platform.id)}</span>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{platform.name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {platform.content_type}
                    </p>
                  </div>
                  {isSelected && (
                    <div className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500 text-white">
                      ✓
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <Badge
                    className={`${getIntentColor(platform.intent)} text-white`}
                  >
                    {platform.intent}
                  </Badge>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
