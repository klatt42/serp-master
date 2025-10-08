import { useState } from 'react';
import { FileText, TrendingUp, Link2, Hash } from 'lucide-react';

interface OptimizationScore {
  category: string;
  score: number;
  suggestion: string;
  icon: typeof FileText;
}

export default function ContentOptimizationPanel() {
  const [contentUrl, setContentUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [scores, setScores] = useState<OptimizationScore[]>([
    {
      category: 'Title Tag',
      score: 85,
      suggestion: 'Add target keyword closer to the beginning',
      icon: FileText,
    },
    {
      category: 'Meta Description',
      score: 60,
      suggestion: 'Include a call-to-action and target keyword',
      icon: FileText,
    },
    {
      category: 'Header Structure',
      score: 90,
      suggestion: 'Good H1-H6 hierarchy, well organized',
      icon: Hash,
    },
    {
      category: 'Keyword Density',
      score: 45,
      suggestion: 'Target keyword appears too frequently (3.2%)',
      icon: Hash,
    },
    {
      category: 'Internal Links',
      score: 70,
      suggestion: 'Add 2-3 more relevant internal links',
      icon: Link2,
    },
    {
      category: 'Content Length',
      score: 80,
      suggestion: 'Good length at 1,850 words for target keyword',
      icon: FileText,
    },
  ]);

  const overallScore = Math.round(scores.reduce((acc, s) => acc + s.score, 0) / scores.length);

  const handleAnalyze = async () => {
    if (!contentUrl.trim()) return;

    setIsAnalyzing(true);

    try {
      const response = await fetch('http://localhost:8000/api/seo/content/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: contentUrl, target_keywords: [] }),
      });

      const data = await response.json();

      if (data.success && data.scores) {
        // Map icon strings back to icon components
        const mappedScores = data.scores.map((score: any) => ({
          ...score,
          icon: score.icon === 'Link2' ? Link2 : score.icon === 'Hash' ? Hash : FileText,
        }));
        setScores(mappedScores);
      }
    } catch (error) {
      console.error('Content optimization error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Content Optimization</h2>
          <p className="text-sm text-gray-600 mt-1">Maximize your content's SEO potential</p>
        </div>
        <FileText className="text-green-500" size={32} />
      </div>

      {/* URL Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Page URL or content to optimize
        </label>
        <div className="flex gap-2">
          <input
            type="url"
            value={contentUrl}
            onChange={(e) => setContentUrl(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
            placeholder="https://your-website.com/blog-post"
            className="input flex-1"
            disabled={isAnalyzing}
          />
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="btn-primary min-w-[120px]"
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>

      {/* Overall Score Card */}
      <div className="mb-6 p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Content Score</h3>
            <p className="text-sm text-gray-600 mt-1">{scores.length} optimization factors analyzed</p>
          </div>
          <div className="text-center">
            <div className={`text-4xl font-bold ${getScoreColor(overallScore)}`}>{overallScore}</div>
            <div className="text-sm text-gray-600">/100</div>
          </div>
        </div>

        {/* Score breakdown visualization */}
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${getProgressColor(overallScore)} transition-all duration-500`}
              style={{ width: `${overallScore}%` }}
            />
          </div>
          <span className="text-sm font-medium text-gray-700">{overallScore}%</span>
        </div>
      </div>

      {/* Optimization Scores */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Optimization Breakdown</h3>

        {scores.map((item, index) => {
          const Icon = item.icon;
          return (
            <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-all">
              <div className="flex items-start gap-3">
                <div className="mt-1">
                  <Icon className="text-gray-400" size={18} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">{item.category}</h4>
                    <span className={`text-xl font-bold ${getScoreColor(item.score)}`}>
                      {item.score}/100
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="mb-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getProgressColor(item.score)} transition-all duration-500`}
                      style={{ width: `${item.score}%` }}
                    />
                  </div>

                  <p className="text-sm text-gray-600">{item.suggestion}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Suggestions */}
      <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
        <div className="flex items-start gap-2">
          <TrendingUp className="text-green-600 mt-0.5" size={18} />
          <div>
            <h4 className="font-semibold text-green-900 text-sm">AI-Powered Suggestions</h4>
            <p className="text-sm text-green-800 mt-1">
              Ask the assistant to "Generate an optimized title" or "Suggest internal linking opportunities" for AI-powered improvements.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
