import React from 'react';
import StatusPanel from './components/StatusPanel';
import KeywordResearchDashboard from './components/KeywordResearchDashboard';
import SimpleChatAssistant from './components/SimpleChatAssistant';
import { BarChart3, Sparkles } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">SERP-Master</h1>
                <p className="text-sm text-gray-600 mt-1">
                  AI-Powered SEO Tool for Small Businesses
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg">
                <Sparkles className="text-blue-600" size={16} />
                <span className="text-sm font-medium text-blue-700">v1.0 Beta</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Status Panel */}
          <StatusPanel />

          {/* Keyword Research Dashboard */}
          <KeywordResearchDashboard />
        </div>

        {/* Info Section */}
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-3 text-gray-800">
            Welcome to SERP-Master! 🚀
          </h2>
          <div className="text-gray-700 space-y-2">
            <p>
              <strong>Getting Started:</strong> Click the AI assistant button (bottom right)
              to get help with SEO tasks.
            </p>
            <p>
              <strong>Features:</strong> Keyword research, technical SEO audits,
              content optimization, and Google Discover optimization.
            </p>
            <p className="text-sm text-gray-600">
              💡 Try asking: "What keywords should I target?" or "Help me optimize my content"
            </p>
          </div>
        </div>
      </main>

      {/* AI Chat Assistant */}
      <SimpleChatAssistant />
    </div>
  );
}

export default App;
