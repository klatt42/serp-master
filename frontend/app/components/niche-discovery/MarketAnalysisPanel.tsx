"use client";

import { NicheAnalysis } from '@/types/niche';
import { TrendingUp, Target, DollarSign, Users, AlertCircle, Lightbulb } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface MarketAnalysisPanelProps {
  analysis: NicheAnalysis;
}

export function MarketAnalysisPanel({ analysis }: MarketAnalysisPanelProps) {

  const marketSizeConfig = {
    small: { color: 'bg-yellow-100 text-yellow-800', label: 'Small Market' },
    medium: { color: 'bg-blue-100 text-blue-800', label: 'Medium Market' },
    large: { color: 'bg-green-100 text-green-800', label: 'Large Market' },
    huge: { color: 'bg-purple-100 text-purple-800', label: 'Huge Market' },
  };

  const competitionConfig = {
    low: { color: 'bg-green-100 text-green-800', label: 'Low Competition' },
    medium: { color: 'bg-yellow-100 text-yellow-800', label: 'Medium Competition' },
    high: { color: 'bg-orange-100 text-orange-800', label: 'High Competition' },
    very_high: { color: 'bg-red-100 text-red-800', label: 'Very High Competition' },
  };

  // Pie chart data for opportunities
  const opportunityData = analysis.opportunities.slice(0, 5).map(opp => ({
    name: opp.cluster_name,
    value: opp.opportunity_score,
  }));

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Market Size */}
        <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Market Size</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-2">
            {analysis.total_search_volume.toLocaleString()}
          </div>
          <span className={`text-xs px-2 py-1 rounded-full font-semibold ${marketSizeConfig[analysis.market_size].color}`}>
            {marketSizeConfig[analysis.market_size].label}
          </span>
        </div>

        {/* Competition */}
        <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="h-5 w-5 text-orange-600" />
            <span className="text-sm font-medium text-gray-700">Competition</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-2">
            {Math.round(analysis.avg_keyword_difficulty)}/100
          </div>
          <span className={`text-xs px-2 py-1 rounded-full font-semibold ${competitionConfig[analysis.competition_level].color}`}>
            {competitionConfig[analysis.competition_level].label}
          </span>
        </div>

        {/* Monetization */}
        <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-gray-700">Monetization</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-2">
            ${analysis.monetization_potential.toFixed(0)}
          </div>
          <span className="text-xs text-gray-600">
            Total CPC Value
          </span>
        </div>

        {/* Confidence */}
        <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium text-gray-700">Confidence</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-2">
            {Math.round(analysis.confidence_score * 100)}%
          </div>
          <span className="text-xs text-gray-600">
            Data Quality
          </span>
        </div>
      </div>

      {/* Strategy Recommendation */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200 p-6">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Lightbulb className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Recommended Strategy</h3>
            <p className="text-gray-700 leading-relaxed">
              {analysis.recommended_strategy}
            </p>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Opportunities Chart */}
        <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Top Cluster Opportunities</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={opportunityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => entry.name}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {opportunityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* SERP Features */}
        <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Common SERP Features</h3>
          <div className="space-y-3">
            {analysis.top_serp_features.map((feature) => (
              <div key={feature} className="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-200">
                <span className="font-medium text-purple-900">{feature}</span>
                <span className="text-xs px-2 py-1 bg-purple-200 text-purple-800 rounded-full font-semibold">
                  Common
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Analysis Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-1">
              {analysis.total_keywords}
            </div>
            <div className="text-sm text-gray-600">Keywords Analyzed</div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">
              {analysis.cluster_count}
            </div>
            <div className="text-sm text-gray-600">Clusters Found</div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-1">
              {analysis.content_gaps.length}
            </div>
            <div className="text-sm text-gray-600">Content Gaps</div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600 mb-1">
              {analysis.opportunities.length}
            </div>
            <div className="text-sm text-gray-600">Opportunities</div>
          </div>
        </div>
      </div>
    </div>
  );
}
