import { useState } from 'react';
import { useCopilotAction, useCopilotReadable } from '@copilotkit/react-core';
import { Search, TrendingUp, BarChart3, Target } from 'lucide-react';
import './SERPMasterDashboard.css';

interface SEOData {
  keywords: string[];
  competition: number;
  volume: number;
  difficulty: number;
}

export function SERPMasterDashboard() {
  const [seoData, setSeoData] = useState<SEOData>({
    keywords: [],
    competition: 0,
    volume: 0,
    difficulty: 0,
  });

  const [activeView, setActiveView] = useState<'overview' | 'keywords' | 'competitors' | 'rankings'>('overview');

  // Make SEO data readable by CopilotKit
  useCopilotReadable({
    description: 'Current SEO data and metrics',
    value: seoData,
  });

  // Define actions the AI assistant can perform
  useCopilotAction({
    name: 'analyzeKeyword',
    description: 'Analyze a keyword for SEO opportunities',
    parameters: [
      {
        name: 'keyword',
        type: 'string',
        description: 'The keyword to analyze',
        required: true,
      },
    ],
    handler: async ({ keyword }) => {
      // This will be connected to DataForSEO API later
      const mockData: SEOData = {
        keywords: [keyword, `${keyword} tips`, `best ${keyword}`],
        competition: Math.floor(Math.random() * 100),
        volume: Math.floor(Math.random() * 10000),
        difficulty: Math.floor(Math.random() * 100),
      };
      setSeoData(mockData);
      return `Analyzed keyword "${keyword}". Found ${mockData.keywords.length} related keywords with ${mockData.volume} monthly search volume.`;
    },
  });

  useCopilotAction({
    name: 'switchView',
    description: 'Switch between different dashboard views',
    parameters: [
      {
        name: 'view',
        type: 'string',
        description: 'The view to switch to: overview, keywords, competitors, or rankings',
        required: true,
      },
    ],
    handler: async ({ view }) => {
      setActiveView(view as any);
      return `Switched to ${view} view`;
    },
  });

  return (
    <div className="serp-master-dashboard">
      <header className="dashboard-header">
        <h1>🎯 SERP Master</h1>
        <p>AI-Powered SEO Intelligence Platform</p>
      </header>

      <nav className="dashboard-nav">
        <button
          className={activeView === 'overview' ? 'active' : ''}
          onClick={() => setActiveView('overview')}
        >
          <BarChart3 size={20} />
          Overview
        </button>
        <button
          className={activeView === 'keywords' ? 'active' : ''}
          onClick={() => setActiveView('keywords')}
        >
          <Search size={20} />
          Keywords
        </button>
        <button
          className={activeView === 'competitors' ? 'active' : ''}
          onClick={() => setActiveView('competitors')}
        >
          <Target size={20} />
          Competitors
        </button>
        <button
          className={activeView === 'rankings' ? 'active' : ''}
          onClick={() => setActiveView('rankings')}
        >
          <TrendingUp size={20} />
          Rankings
        </button>
      </nav>

      <main className="dashboard-content">
        {activeView === 'overview' && (
          <div className="overview-section">
            <h2>SEO Overview</h2>
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>Keywords Tracked</h3>
                <p className="metric-value">{seoData.keywords.length}</p>
              </div>
              <div className="metric-card">
                <h3>Search Volume</h3>
                <p className="metric-value">{seoData.volume.toLocaleString()}</p>
              </div>
              <div className="metric-card">
                <h3>Competition</h3>
                <p className="metric-value">{seoData.competition}%</p>
              </div>
              <div className="metric-card">
                <h3>Difficulty</h3>
                <p className="metric-value">{seoData.difficulty}%</p>
              </div>
            </div>
            <div className="welcome-message">
              <h3>👋 Welcome to SERP Master</h3>
              <p>Use the AI assistant on the right to:</p>
              <ul>
                <li>Analyze keywords and find SEO opportunities</li>
                <li>Research competitors and their strategies</li>
                <li>Track rankings and monitor performance</li>
                <li>Get AI-powered SEO recommendations</li>
              </ul>
              <p className="tip">💡 Try asking: "Analyze the keyword 'react tutorials'"</p>
            </div>
          </div>
        )}

        {activeView === 'keywords' && (
          <div className="keywords-section">
            <h2>Keyword Analysis</h2>
            {seoData.keywords.length > 0 ? (
              <div className="keywords-list">
                {seoData.keywords.map((keyword, index) => (
                  <div key={index} className="keyword-item">
                    <span className="keyword-text">{keyword}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">Ask the AI assistant to analyze a keyword to get started!</p>
            )}
          </div>
        )}

        {activeView === 'competitors' && (
          <div className="competitors-section">
            <h2>Competitor Analysis</h2>
            <p className="empty-state">Competitor analysis coming soon! Ask the AI assistant for help.</p>
          </div>
        )}

        {activeView === 'rankings' && (
          <div className="rankings-section">
            <h2>Ranking Tracker</h2>
            <p className="empty-state">Ranking tracking coming soon! Ask the AI assistant for help.</p>
          </div>
        )}
      </main>
    </div>
  );
}
