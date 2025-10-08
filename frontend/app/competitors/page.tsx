"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Loader2, TrendingUp, AlertCircle, Target, BarChart } from "lucide-react";

interface CompetitorAnalysisRequest {
  your_brand: string;
  competitor_brands: string[];
  platforms: string[];
  keywords: string[];
  location: string;
}

interface CompetitorAnalysisResult {
  overall_positioning: {
    your_score: number;
    competitor_scores: { [key: string]: number };
    platform_breakdown: { [key: string]: any };
  };
  opportunities: Array<{
    keyword: string;
    platforms: string[];
    reason: string;
    priority: string;
    estimated_difficulty: string;
  }>;
  competitive_gaps: Array<{
    gap_type: string;
    description: string;
    platforms: string[];
    impact: string;
    recommendation: string;
  }>;
  platform_insights: { [key: string]: any };
}

export default function CompetitorsPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<CompetitorAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [yourBrand, setYourBrand] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [keywords, setKeywords] = useState("");
  const [location, setLocation] = useState("United States");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([
    "youtube",
    "tiktok",
    "amazon",
    "google",
    "reddit",
  ]);

  const availablePlatforms = [
    { id: "youtube", name: "YouTube" },
    { id: "tiktok", name: "TikTok" },
    { id: "amazon", name: "Amazon" },
    { id: "google", name: "Google" },
    { id: "reddit", name: "Reddit" },
  ];

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platformId)
        ? prev.filter((p) => p !== platformId)
        : [...prev, platformId]
    );
  };

  const analyzeCompetitors = async () => {
    if (!yourBrand.trim() || !competitors.trim() || !keywords.trim()) {
      setError("Please fill in all required fields");
      return;
    }

    if (selectedPlatforms.length === 0) {
      setError("Please select at least one platform");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const requestData: CompetitorAnalysisRequest = {
        your_brand: yourBrand.trim(),
        competitor_brands: competitors.split(",").map((c) => c.trim()),
        platforms: selectedPlatforms,
        keywords: keywords.split(",").map((k) => k.trim()),
        location: location,
      };

      const response = await fetch("http://localhost:8000/api/competitive/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
      console.error("Competitor analysis error:", err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case "high":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "medium":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "low":
        return "bg-gray-100 text-gray-800 border-gray-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Competitive Intelligence</h1>
        <p className="text-gray-600">
          Analyze your competitors across multiple platforms and discover opportunities
        </p>
      </div>

      {/* Input Form */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Competitor Analysis Setup</CardTitle>
          <CardDescription>
            Enter your brand and competitor information to get started
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="yourBrand">Your Brand Name *</Label>
              <Input
                id="yourBrand"
                placeholder="e.g., MyBrand"
                value={yourBrand}
                onChange={(e) => setYourBrand(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="e.g., United States"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="competitors">Competitor Brands * (comma-separated)</Label>
            <Input
              id="competitors"
              placeholder="e.g., Competitor1, Competitor2, Competitor3"
              value={competitors}
              onChange={(e) => setCompetitors(e.target.value)}
            />
            <p className="text-sm text-gray-500">Enter up to 10 competitor brands</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="keywords">Keywords to Track * (comma-separated)</Label>
            <Input
              id="keywords"
              placeholder="e.g., best running shoes, marathon training, trail running"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
            <p className="text-sm text-gray-500">Enter up to 50 keywords</p>
          </div>

          <div className="space-y-2">
            <Label>Platforms to Analyze</Label>
            <div className="flex flex-wrap gap-2">
              {availablePlatforms.map((platform) => (
                <Badge
                  key={platform.id}
                  variant={selectedPlatforms.includes(platform.id) ? "default" : "outline"}
                  className="cursor-pointer px-4 py-2"
                  onClick={() => togglePlatform(platform.id)}
                >
                  {platform.name}
                </Badge>
              ))}
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <Button
            onClick={analyzeCompetitors}
            disabled={loading}
            className="w-full md:w-auto"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing Competitors...
              </>
            ) : (
              <>
                <BarChart className="mr-2 h-4 w-4" />
                Analyze Competitors
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Overall Positioning */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Overall Competitive Positioning
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-gray-600 mb-1">Your Score</p>
                  <p className="text-3xl font-bold text-blue-600">
                    {results.overall_positioning.your_score}
                  </p>
                </div>

                {Object.entries(results.overall_positioning.competitor_scores).map(
                  ([competitor, score]) => (
                    <div
                      key={competitor}
                      className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <p className="text-sm text-gray-600 mb-1">{competitor}</p>
                      <p className="text-3xl font-bold text-gray-700">{score}</p>
                    </div>
                  )
                )}
              </div>

              {/* Platform Breakdown */}
              <div className="mt-6">
                <h4 className="font-semibold mb-3">Platform Breakdown</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(results.overall_positioning.platform_breakdown).map(
                    ([platform, data]: [string, any]) => (
                      <div
                        key={platform}
                        className="p-4 bg-white rounded-lg border border-gray-200"
                      >
                        <p className="font-medium capitalize mb-2">{platform}</p>
                        <div className="space-y-1 text-sm">
                          <p className="text-gray-600">
                            Your Score: <span className="font-semibold">{data.your_score}</span>
                          </p>
                          <p className="text-gray-600">
                            Avg Competitor:{" "}
                            <span className="font-semibold">{data.avg_competitor_score}</span>
                          </p>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Opportunities */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Content Opportunities ({results.opportunities.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.opportunities.map((opportunity, index) => (
                  <div
                    key={index}
                    className="p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-lg">{opportunity.keyword}</h4>
                      <div className="flex gap-2">
                        <Badge className={getPriorityColor(opportunity.priority)}>
                          {opportunity.priority} Priority
                        </Badge>
                        <Badge variant="outline">{opportunity.estimated_difficulty}</Badge>
                      </div>
                    </div>
                    <p className="text-gray-600 mb-3">{opportunity.reason}</p>
                    <div className="flex flex-wrap gap-2">
                      {opportunity.platforms.map((platform) => (
                        <Badge key={platform} variant="secondary" className="capitalize">
                          {platform}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}

                {results.opportunities.length === 0 && (
                  <p className="text-gray-500 text-center py-8">
                    No opportunities identified. Your content coverage is strong!
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Competitive Gaps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Competitive Gaps ({results.competitive_gaps.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.competitive_gaps.map((gap, index) => (
                  <div
                    key={index}
                    className="p-4 bg-white rounded-lg border border-gray-200 hover:border-yellow-300 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-lg">{gap.gap_type}</h4>
                      <Badge className={getImpactColor(gap.impact)}>{gap.impact} Impact</Badge>
                    </div>
                    <p className="text-gray-600 mb-2">{gap.description}</p>
                    <div className="mb-3 flex flex-wrap gap-2">
                      {gap.platforms.map((platform) => (
                        <Badge key={platform} variant="secondary" className="capitalize">
                          {platform}
                        </Badge>
                      ))}
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded p-3">
                      <p className="text-sm font-medium text-blue-900 mb-1">Recommendation:</p>
                      <p className="text-sm text-blue-800">{gap.recommendation}</p>
                    </div>
                  </div>
                ))}

                {results.competitive_gaps.length === 0 && (
                  <p className="text-gray-500 text-center py-8">
                    No significant gaps identified. You're well-positioned!
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Platform Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Platform-Specific Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(results.platform_insights).map(([platform, insights]: [string, any]) => (
                  <div
                    key={platform}
                    className="p-4 bg-white rounded-lg border border-gray-200"
                  >
                    <h4 className="font-semibold capitalize mb-3">{platform}</h4>
                    <div className="space-y-2 text-sm">
                      {Object.entries(insights).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-600 capitalize">
                            {key.replace(/_/g, " ")}:
                          </span>
                          <span className="font-medium">
                            {typeof value === "object" ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
