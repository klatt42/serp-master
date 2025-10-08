"use client";

import { TrendingUp, Target, Brain, MapPin, Users, Heart } from 'lucide-react';
import { RadialBarChart, RadialBar, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ScoreDashboardProps {
  auditResults: {
    total_score: number;
    max_score: number;
    percentage: number;
    grade: string;
    component_scores: {
      seo: { score: number; max: number; percentage: number };
      aeo: { score: number; max: number; percentage: number };
      geo: { score: number; max: number; percentage: number };
    };
  };
  competitorScores?: Array<{ name: string; score: number }>;
}

export default function ScoreDashboard({ auditResults, competitorScores }: ScoreDashboardProps) {

  // Get grade color
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-green-600 bg-green-100';
      case 'B': return 'text-blue-600 bg-blue-100';
      case 'C': return 'text-yellow-600 bg-yellow-100';
      case 'D': return 'text-orange-600 bg-orange-100';
      case 'F': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // Get percentage color
  const getPercentageColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg shadow-xl p-8 text-white animate-slide-up">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="mb-6 md:mb-0">
            <h2 className="text-lg font-medium opacity-90 mb-2">Overall SEO Score</h2>
            <div className="flex items-baseline space-x-3">
              <span className="text-6xl font-bold">{auditResults.total_score}</span>
              <span className="text-3xl opacity-75">/ {auditResults.max_score}</span>
            </div>
            <div className="mt-3 flex items-center space-x-3">
              <div className={`px-4 py-2 rounded-full font-bold text-xl ${getGradeColor(auditResults.grade)}`}>
                Grade: {auditResults.grade}
              </div>
              <span className="text-lg opacity-90">{auditResults.percentage.toFixed(1)}%</span>
            </div>
          </div>

          {/* Progress Circle */}
          <div className="relative w-48 h-48">
            <svg className="transform -rotate-90 w-48 h-48">
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="rgba(255,255,255,0.2)"
                strokeWidth="12"
                fill="none"
              />
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="white"
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 88}`}
                strokeDashoffset={`${2 * Math.PI * 88 * (1 - auditResults.percentage / 100)}`}
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-3xl font-bold">{auditResults.percentage.toFixed(0)}%</div>
                <div className="text-sm opacity-75">Complete</div>
              </div>
            </div>
          </div>
        </div>

        {/* Percentage Bar */}
        <div className="mt-6">
          <div className="w-full bg-white bg-opacity-20 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-1000 ease-out ${getPercentageColor(auditResults.percentage)}`}
              style={{ width: `${auditResults.percentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Dimensional Score Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ScoreGauge
          title="Traditional SEO"
          score={auditResults.component_scores.seo.score}
          maxScore={auditResults.component_scores.seo.max}
          percentage={auditResults.component_scores.seo.percentage}
          icon={<Target className="w-6 h-6" />}
          color="#3B82F6"
          available={true}
        />
        <ScoreGauge
          title="AEO Score"
          score={auditResults.component_scores.aeo.score}
          maxScore={auditResults.component_scores.aeo.max}
          percentage={auditResults.component_scores.aeo.percentage}
          icon={<Brain className="w-6 h-6" />}
          color="#10B981"
          available={true}
        />
        <ScoreGauge
          title="GEO Score"
          score={auditResults.component_scores.geo.score}
          maxScore={auditResults.component_scores.geo.max}
          percentage={auditResults.component_scores.geo.percentage}
          icon={<MapPin className="w-6 h-6" />}
          color="#6B7280"
          available={false}
          comingSoon={true}
        />
      </div>

      {/* Placeholder for future dimensions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-50">
        <ScoreGauge
          title="Platform Presence"
          score={0}
          maxScore={10}
          percentage={0}
          icon={<Users className="w-6 h-6" />}
          color="#6B7280"
          available={false}
          comingSoon={true}
        />
        <ScoreGauge
          title="Engagement Signals"
          score={0}
          maxScore={10}
          percentage={0}
          icon={<Heart className="w-6 h-6" />}
          color="#6B7280"
          available={false}
          comingSoon={true}
        />
      </div>

      {/* Score Breakdown Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Score Breakdown</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={[
              {
                name: 'Traditional SEO',
                current: auditResults.component_scores.seo.score,
                max: auditResults.component_scores.seo.max,
                percentage: auditResults.component_scores.seo.percentage,
              },
              {
                name: 'AEO Score',
                current: auditResults.component_scores.aeo.score,
                max: auditResults.component_scores.aeo.max,
                percentage: auditResults.component_scores.aeo.percentage,
              },
              {
                name: 'GEO Score',
                current: auditResults.component_scores.geo.score,
                max: auditResults.component_scores.geo.max,
                percentage: auditResults.component_scores.geo.percentage,
              },
            ]}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 50]} />
            <YAxis dataKey="name" type="category" />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 rounded shadow-lg border border-gray-200">
                      <p className="font-semibold text-gray-900">{data.name}</p>
                      <p className="text-sm text-gray-600">
                        Score: {data.current} / {data.max}
                      </p>
                      <p className="text-sm text-gray-600">
                        {data.percentage.toFixed(1)}%
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="current" fill="#3B82F6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Competitor Comparison (if provided) */}
      {competitorScores && competitorScores.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Competitor Comparison</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border-2 border-blue-200">
              <span className="font-semibold text-gray-900">Your Site</span>
              <span className="text-2xl font-bold text-blue-600">{auditResults.total_score}</span>
            </div>
            {competitorScores.map((competitor, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <span className="text-gray-700">{competitor.name}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-xl font-semibold text-gray-900">{competitor.score}</span>
                  {competitor.score < auditResults.total_score && (
                    <TrendingUp className="w-5 h-5 text-green-500" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface ScoreGaugeProps {
  title: string;
  score: number;
  maxScore: number;
  percentage: number;
  icon: React.ReactNode;
  color: string;
  available: boolean;
  comingSoon?: boolean;
}

function ScoreGauge({ title, score, maxScore, percentage, icon, color, available, comingSoon }: ScoreGaugeProps) {
  const gaugeData = [
    {
      name: title,
      value: percentage,
      fill: available ? color : '#D1D5DB',
    },
  ];

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${!available ? 'opacity-60' : ''}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div style={{ color }} className="p-2 bg-gray-50 rounded-lg">
            {icon}
          </div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
        </div>
        {comingSoon && (
          <span className="px-2 py-1 text-xs font-semibold bg-gray-200 text-gray-600 rounded-full">
            Coming Soon
          </span>
        )}
      </div>

      {/* Radial Gauge */}
      <div className="relative h-40 flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="60%"
            outerRadius="90%"
            data={gaugeData}
            startAngle={180}
            endAngle={0}
          >
            <RadialBar
              background
              dataKey="value"
              cornerRadius={10}
              fill={available ? color : '#D1D5DB'}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">{score}</div>
            <div className="text-sm text-gray-500">/ {maxScore}</div>
          </div>
        </div>
      </div>

      {/* Score Details */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Percentage</span>
          <span className={`text-sm font-semibold ${available ? 'text-gray-900' : 'text-gray-500'}`}>
            {percentage.toFixed(1)}%
          </span>
        </div>
        {available && (
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all duration-1000 ease-out"
              style={{
                width: `${percentage}%`,
                backgroundColor: color,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
