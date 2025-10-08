import AuditInputForm from './components/AuditInputForm';
import { Target, Zap, Shield, Brain, Users } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          {/* Header */}
          <div className="text-center mb-12 animate-slide-down">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
              Know Where You Stand.
              <span className="block text-blue-600 mt-2">Find Where to Compete.</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Modern SEO analysis for small businesses. Get instant insights into your website&apos;s performance with AI-powered recommendations.
            </p>
          </div>

          {/* Audit Input Form */}
          <AuditInputForm />

          {/* Additional Tools */}
          <div className="mt-8 flex flex-col sm:flex-row justify-center items-center gap-4">
            <Link
              href="/compare"
              className="inline-flex items-center px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
            >
              <Users className="w-5 h-5 mr-2" />
              Compare Against Competitors
            </Link>
            <Link
              href="/platform-strategy"
              className="inline-flex items-center px-6 py-3 border-2 border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors font-medium"
            >
              <Brain className="w-5 h-5 mr-2" />
              Multi-Platform Strategy
            </Link>
          </div>
          <p className="mt-3 text-sm text-gray-500 text-center">
            Benchmark against competitors or discover cross-platform content opportunities
          </p>

          {/* Features List */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <FeatureCard
              icon={<Target className="h-6 w-6 text-blue-600" />}
              title="Traditional SEO"
              description="30 points covering technical SEO, on-page optimization, and site structure"
            />
            <FeatureCard
              icon={<Brain className="h-6 w-6 text-green-600" />}
              title="AEO Scoring"
              description="25 points for Answer Engine Optimization - voice search and AI assistants"
            />
            <FeatureCard
              icon={<Shield className="h-6 w-6 text-purple-600" />}
              title="Entity Clarity"
              description="Unique feature that analyzes how AI understands your business identity"
              badge="UNIQUE"
            />
            <FeatureCard
              icon={<Zap className="h-6 w-6 text-yellow-600" />}
              title="Quick Wins"
              description="High-impact, low-effort recommendations to boost your score fast"
            />
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <StepCard
              number="1"
              title="Enter Your URL"
              description="Simply paste your website URL and click 'Start Audit'. We'll crawl up to 100 pages to analyze your entire site."
            />
            <StepCard
              number="2"
              title="AI Analyzes"
              description="Our AI engine examines your SEO, content structure, entity clarity, and schema markup in real-time."
            />
            <StepCard
              number="3"
              title="Get Recommendations"
              description="Receive a detailed score breakdown with prioritized, actionable recommendations to improve your rankings."
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h3 className="text-xl font-bold">SERP-Master</h3>
              <p className="text-gray-400 text-sm mt-1">Modern SEO analysis powered by AI</p>
            </div>
            <div className="flex space-x-6 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors">About</a>
              <a href="#" className="hover:text-white transition-colors">Pricing</a>
              <a href="#" className="hover:text-white transition-colors">Docs</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-gray-800 text-center text-sm text-gray-400">
            <p>&copy; 2025 SERP-Master. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  badge?: string;
}

function FeatureCard({ icon, title, description, badge }: FeatureCardProps) {
  return (
    <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        <div className="p-2 bg-gray-50 rounded-lg">
          {icon}
        </div>
        {badge && (
          <span className="px-2 py-1 text-xs font-semibold bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full">
            {badge}
          </span>
        )}
      </div>
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}

interface StepCardProps {
  number: string;
  title: string;
  description: string;
}

function StepCard({ number, title, description }: StepCardProps) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold text-xl mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
