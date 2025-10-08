import { useState } from 'react';
import { AlertCircle, CheckCircle, Clock, Smartphone, Zap } from 'lucide-react';

interface AuditIssue {
  category: string;
  severity: 'error' | 'warning' | 'success';
  score: number;
  message: string;
}

export default function TechnicalAuditPanel() {
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditResults, setAuditResults] = useState<AuditIssue[]>([
    { category: 'Page Speed', severity: 'warning', score: 78, message: 'Optimize images and enable compression' },
    { category: 'Mobile Friendly', severity: 'success', score: 95, message: 'All pages are mobile responsive' },
    { category: 'Core Web Vitals', severity: 'error', score: 45, message: 'LCP and CLS need improvement' },
    { category: 'SSL Certificate', severity: 'success', score: 100, message: 'HTTPS properly configured' },
    { category: 'Schema Markup', severity: 'warning', score: 60, message: 'Missing structured data on some pages' },
  ]);

  const handleAudit = async () => {
    if (!websiteUrl.trim()) return;

    setIsAuditing(true);

    try {
      const response = await fetch('http://localhost:8000/api/seo/audit/technical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: websiteUrl }),
      });

      const data = await response.json();

      if (data.success && data.results) {
        setAuditResults(data.results);
      }
    } catch (error) {
      console.error('Technical audit error:', error);
    } finally {
      setIsAuditing(false);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'success':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'warning':
        return <AlertCircle className="text-yellow-500" size={20} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={20} />;
      default:
        return <Clock className="text-gray-500" size={20} />;
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const overallScore = Math.round(auditResults.reduce((acc, r) => acc + r.score, 0) / auditResults.length);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Technical SEO Audit</h2>
          <p className="text-sm text-gray-600 mt-1">Comprehensive site health analysis</p>
        </div>
        <Zap className="text-purple-500" size={32} />
      </div>

      {/* URL Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Website URL to audit
        </label>
        <div className="flex gap-2">
          <input
            type="url"
            value={websiteUrl}
            onChange={(e) => setWebsiteUrl(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAudit()}
            placeholder="https://your-website.com"
            className="input flex-1"
            disabled={isAuditing}
          />
          <button
            onClick={handleAudit}
            disabled={isAuditing}
            className="btn-primary min-w-[120px]"
          >
            {isAuditing ? 'Auditing...' : 'Audit Site'}
          </button>
        </div>
      </div>

      {/* Overall Score */}
      <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Overall SEO Health Score</h3>
            <p className="text-sm text-gray-600 mt-1">Based on {auditResults.length} key factors</p>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600">{overallScore}</div>
            <div className="text-sm text-gray-600">/100</div>
          </div>
        </div>
      </div>

      {/* Audit Results */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Audit Results</h3>

        {auditResults.map((result, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border transition-all hover:shadow-md ${getSeverityBg(result.severity)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                {getSeverityIcon(result.severity)}
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-semibold text-gray-900">{result.category}</h4>
                    <span className="text-lg font-bold text-gray-900">{result.score}/100</span>
                  </div>
                  <p className="text-sm text-gray-600">{result.message}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Action Items */}
      <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
        <div className="flex items-start gap-2">
          <Smartphone className="text-purple-600 mt-0.5" size={18} />
          <div>
            <h4 className="font-semibold text-purple-900 text-sm">Priority Actions</h4>
            <p className="text-sm text-purple-800 mt-1">
              Focus on improving Core Web Vitals and page speed for immediate SEO gains. Ask the AI assistant for specific optimization steps.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
