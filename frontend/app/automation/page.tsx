"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BarChart,
  TrendingUp,
  RefreshCw,
  CheckCircle,
  Users,
  Lightbulb,
  Activity
} from "lucide-react";

export default function AutomationPage() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Content Automation Intelligence</h1>
        <p className="text-gray-600">
          AI-powered workflow automation and performance optimization
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6 mb-8">
          <TabsTrigger value="overview">
            <Activity className="mr-2 h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="performance">
            <BarChart className="mr-2 h-4 w-4" />
            Performance
          </TabsTrigger>
          <TabsTrigger value="topics">
            <Lightbulb className="mr-2 h-4 w-4" />
            Topics
          </TabsTrigger>
          <TabsTrigger value="tests">
            <TrendingUp className="mr-2 h-4 w-4" />
            A/B Tests
          </TabsTrigger>
          <TabsTrigger value="refresh">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </TabsTrigger>
          <TabsTrigger value="workflow">
            <CheckCircle className="mr-2 h-4 w-4" />
            Workflow
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart className="h-5 w-5 text-blue-600" />
                  Performance Tracking
                </CardTitle>
                <CardDescription>
                  Monitor content effectiveness and ROI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Performance Score</span>
                    <Badge>75/100</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Content Tracked</span>
                    <Badge variant="outline">0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Top Performers</span>
                    <Badge variant="secondary">0</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-yellow-600" />
                  AI Topic Suggestions
                </CardTitle>
                <CardDescription>
                  Data-driven content recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Suggestions Generated</span>
                    <Badge>0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">High Priority</span>
                    <Badge variant="outline">0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Confidence</span>
                    <Badge variant="secondary">0%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  A/B Testing
                </CardTitle>
                <CardDescription>
                  Optimize content through testing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Tests</span>
                    <Badge>0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completed Tests</span>
                    <Badge variant="outline">0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Improvement</span>
                    <Badge variant="secondary">0%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <RefreshCw className="h-5 w-5 text-orange-600" />
                  Content Refresh
                </CardTitle>
                <CardDescription>
                  Identify and update stale content
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Needs Refresh</span>
                    <Badge>0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">High Priority</span>
                    <Badge variant="outline">0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Recently Refreshed</span>
                    <Badge variant="secondary">0</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-purple-600" />
                  Workflow Pipeline
                </CardTitle>
                <CardDescription>
                  Manage content from idea to publish
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">In Progress</span>
                    <Badge>0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Ready for Review</span>
                    <Badge variant="outline">0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Published This Week</span>
                    <Badge variant="secondary">0</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-indigo-600" />
                  Team Collaboration
                </CardTitle>
                <CardDescription>
                  Manage team members and roles
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Team Members</span>
                    <Badge>1</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Projects</span>
                    <Badge variant="outline">0</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pending Invites</span>
                    <Badge variant="secondary">0</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Getting Started with Automation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold mb-2">1. Track Performance</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Start monitoring your content&apos;s ranking, traffic, and engagement metrics
                  </p>
                  <Button size="sm">Track Content</Button>
                </div>

                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold mb-2">2. Get Topic Suggestions</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Let AI analyze your performance and suggest winning topics
                  </p>
                  <Button size="sm">Generate Suggestions</Button>
                </div>

                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold mb-2">3. Run A/B Tests</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Test headlines, descriptions, and content variations
                  </p>
                  <Button size="sm">Create Test</Button>
                </div>

                <div className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold mb-2">4. Automate Workflow</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Organize your content pipeline from idea to publish
                  </p>
                  <Button size="sm">Setup Workflow</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Other tabs would have detailed interfaces */}
        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle>Performance Analytics</CardTitle>
              <CardDescription>
                Track content effectiveness and ROI over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Performance tracking dashboard coming soon. Track metrics like rankings, traffic,
                engagement, and calculate ROI for your content.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="topics">
          <Card>
            <CardHeader>
              <CardTitle>AI Topic Suggestions</CardTitle>
              <CardDescription>
                Data-driven content recommendations based on performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                AI-powered topic suggestion engine coming soon. Get recommendations based on
                successful patterns, keyword opportunities, and competitive gaps.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tests">
          <Card>
            <CardHeader>
              <CardTitle>A/B Testing Manager</CardTitle>
              <CardDescription>
                Test content variations to optimize performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                A/B testing framework coming soon. Test headlines, descriptions, and content
                structures with statistical significance analysis.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="refresh">
          <Card>
            <CardHeader>
              <CardTitle>Content Refresh Queue</CardTitle>
              <CardDescription>
                Identify and prioritize content needing updates
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Content refresh intelligence coming soon. Automatically detect stale content and
                get specific refresh recommendations.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="workflow">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Board</CardTitle>
              <CardDescription>
                Manage content pipeline from idea to publish
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Kanban workflow board coming soon. Track content through 8 stages: Idea, Research,
                Outline, Draft, Review, Revise, Publish, Track.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
