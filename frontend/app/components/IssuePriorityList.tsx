"use client";

import { useState, useMemo } from 'react';
import { AlertCircle, AlertTriangle, Info, Zap, ChevronDown, ChevronUp, Search, Filter, Download, Check, X } from 'lucide-react';

export interface Issue {
  id: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  title: string;
  description: string;
  pages_affected: number;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  recommendation: string;
  quick_win: boolean;
  category: 'SEO' | 'AEO' | 'GEO';
  details?: {
    explanation: string;
    fix_steps: string[];
    code_example?: string;
  };
}

interface IssuePriorityListProps {
  issues?: {
    critical?: Issue[];
    warnings?: Issue[];
    info?: Issue[];
    quick_wins?: Issue[];
  };
  onIssueClick?: (issue: Issue) => void;
  onMarkResolved?: (issueId: string) => void;
}

type TabType = 'critical' | 'warnings' | 'info';
type CategoryFilter = 'ALL' | 'SEO' | 'AEO' | 'GEO';

export default function IssuePriorityList({ issues, onIssueClick, onMarkResolved }: IssuePriorityListProps) {
  // Provide default values for issues if undefined
  const safeIssues = {
    critical: issues?.critical || [],
    warnings: issues?.warnings || [],
    info: issues?.info || [],
    quick_wins: issues?.quick_wins || [],
  };

  const [activeTab, setActiveTab] = useState<TabType>('critical');
  const [expandedIssues, setExpandedIssues] = useState<Set<string>>(new Set());
  const [resolvedIssues, setResolvedIssues] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('ALL');

  // Toggle issue expansion
  const toggleIssue = (issueId: string) => {
    const newExpanded = new Set(expandedIssues);
    if (newExpanded.has(issueId)) {
      newExpanded.delete(issueId);
    } else {
      newExpanded.add(issueId);
    }
    setExpandedIssues(newExpanded);
  };

  // Mark issue as resolved
  const markResolved = (issueId: string) => {
    const newResolved = new Set(resolvedIssues);
    if (newResolved.has(issueId)) {
      newResolved.delete(issueId);
    } else {
      newResolved.add(issueId);
    }
    setResolvedIssues(newResolved);
    if (onMarkResolved) {
      onMarkResolved(issueId);
    }
  };

  // Filter issues by search and category
  const filterIssues = (issueList: Issue[] | undefined) => {
    // Handle undefined or null issueList
    if (!issueList || !Array.isArray(issueList)) {
      return [];
    }

    return issueList.filter(issue => {
      const matchesSearch = searchQuery === '' ||
        issue.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.description.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = categoryFilter === 'ALL' || issue.category === categoryFilter;

      return matchesSearch && matchesCategory;
    });
  };

  // Get filtered issues for current tab
  const currentIssues = useMemo(() => {
    return filterIssues(safeIssues[activeTab]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, safeIssues, searchQuery, categoryFilter]);

  // Export to CSV
  const exportToCSV = () => {
    const allIssues = [
      ...safeIssues.critical,
      ...safeIssues.warnings,
      ...safeIssues.info
    ];
    const csv = [
      ['Severity', 'Title', 'Description', 'Pages Affected', 'Impact', 'Effort', 'Category', 'Quick Win'].join(','),
      ...allIssues.map(issue => [
        issue.severity,
        `"${issue.title}"`,
        `"${issue.description}"`,
        issue.pages_affected,
        issue.impact,
        issue.effort,
        issue.category,
        issue.quick_win ? 'Yes' : 'No'
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'seo-issues.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Get tab counts
  const criticalCount = safeIssues.critical.length;
  const warningsCount = safeIssues.warnings.length;
  const infoCount = safeIssues.info.length;

  return (
    <div className="space-y-6">
      {/* Quick Wins Section */}
      {safeIssues.quick_wins.length > 0 && (
        <div className="sticky top-20 z-20 bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-300 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Zap className="w-6 h-6 text-yellow-600" />
              <h3 className="text-xl font-bold text-gray-900">⚡ Quick Wins - Fix These First!</h3>
            </div>
            <span className="px-3 py-1 bg-yellow-600 text-white rounded-full text-sm font-semibold">
              {safeIssues.quick_wins.length} issue{safeIssues.quick_wins.length !== 1 ? 's' : ''}
            </span>
          </div>

          <div className="space-y-3">
            {safeIssues.quick_wins.slice(0, 5).map((issue, index) => (
              <div
                key={issue.id || `quick-win-${index}`}
                className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-yellow-600 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => {
                  toggleIssue(issue.id);
                  if (onIssueClick) onIssueClick(issue);
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-semibold text-gray-900">{issue.title}</h4>
                      <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                        +{issue.impact} pts
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{issue.description}</p>
                  </div>
                  <div className="ml-4 flex items-center space-x-2">
                    {getEffortBadge(issue.effort)}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        markResolved(issue.id);
                      }}
                      className={`p-1 rounded transition-colors ${
                        resolvedIssues.has(issue.id)
                          ? 'bg-green-100 text-green-600'
                          : 'bg-gray-100 text-gray-400 hover:bg-green-50 hover:text-green-600'
                      }`}
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {expandedIssues.has(issue.id) && issue.details && (
                  <div className="mt-4 pt-4 border-t border-gray-200 animate-slide-down">
                    <IssueDetails issue={issue} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Issues Section */}
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header with Search and Filters */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Issues & Recommendations</h2>
            <button
              onClick={exportToCSV}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </button>
          </div>

          {/* Search Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search issues..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <div className="flex space-x-2">
              {(['ALL', 'SEO', 'AEO', 'GEO'] as CategoryFilter[]).map((category) => (
                <button
                  key={category}
                  onClick={() => setCategoryFilter(category)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    categoryFilter === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex space-x-1 px-6">
            <TabButton
              active={activeTab === 'critical'}
              onClick={() => setActiveTab('critical')}
              icon={<AlertCircle className="w-4 h-4" />}
              label="Critical"
              count={criticalCount}
              color="red"
            />
            <TabButton
              active={activeTab === 'warnings'}
              onClick={() => setActiveTab('warnings')}
              icon={<AlertTriangle className="w-4 h-4" />}
              label="Warnings"
              count={warningsCount}
              color="yellow"
            />
            <TabButton
              active={activeTab === 'info'}
              onClick={() => setActiveTab('info')}
              icon={<Info className="w-4 h-4" />}
              label="Info"
              count={infoCount}
              color="blue"
            />
          </div>
        </div>

        {/* Issue List */}
        <div className="p-6">
          {currentIssues.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-2">
                {searchQuery || categoryFilter !== 'ALL' ? (
                  <>
                    <Search className="w-12 h-12 mx-auto mb-3" />
                    <p className="text-lg font-medium">No issues found</p>
                    <p className="text-sm">Try adjusting your search or filters</p>
                  </>
                ) : (
                  <>
                    <Check className="w-12 h-12 mx-auto mb-3 text-green-500" />
                    <p className="text-lg font-medium text-green-600">No {activeTab} issues!</p>
                    <p className="text-sm text-gray-500">Great job!</p>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {currentIssues.map((issue, index) => (
                <IssueCard
                  key={issue.id || `issue-${activeTab}-${index}`}
                  issue={issue}
                  isExpanded={expandedIssues.has(issue.id || `issue-${activeTab}-${index}`)}
                  isResolved={resolvedIssues.has(issue.id || `issue-${activeTab}-${index}`)}
                  onToggle={() => {
                    toggleIssue(issue.id || `issue-${activeTab}-${index}`);
                    if (onIssueClick) onIssueClick(issue);
                  }}
                  onMarkResolved={() => markResolved(issue.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Tab Button Component
interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  count: number;
  color: 'red' | 'yellow' | 'blue';
}

function TabButton({ active, onClick, icon, label, count, color }: TabButtonProps) {
  const colorClasses = {
    red: {
      active: 'border-red-500 text-red-600',
      inactive: 'border-transparent text-gray-600 hover:text-gray-900',
      badge: 'bg-red-100 text-red-800'
    },
    yellow: {
      active: 'border-yellow-500 text-yellow-600',
      inactive: 'border-transparent text-gray-600 hover:text-gray-900',
      badge: 'bg-yellow-100 text-yellow-800'
    },
    blue: {
      active: 'border-blue-500 text-blue-600',
      inactive: 'border-transparent text-gray-600 hover:text-gray-900',
      badge: 'bg-blue-100 text-blue-800'
    }
  };

  const classes = active ? colorClasses[color].active : colorClasses[color].inactive;

  return (
    <button
      onClick={onClick}
      className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium transition-colors ${classes}`}
    >
      {icon}
      <span>{label}</span>
      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${colorClasses[color].badge}`}>
        {count}
      </span>
    </button>
  );
}

// Issue Card Component
interface IssueCardProps {
  issue: Issue;
  isExpanded: boolean;
  isResolved: boolean;
  onToggle: () => void;
  onMarkResolved: () => void;
}

function IssueCard({ issue, isExpanded, isResolved, onToggle, onMarkResolved }: IssueCardProps) {
  const getSeverityIcon = (severity: Issue['severity']) => {
    switch (severity) {
      case 'CRITICAL':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'WARNING':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'INFO':
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getSeverityColor = (severity: Issue['severity']) => {
    switch (severity) {
      case 'CRITICAL':
        return 'border-l-red-600 bg-red-50';
      case 'WARNING':
        return 'border-l-yellow-600 bg-yellow-50';
      case 'INFO':
        return 'border-l-blue-600 bg-blue-50';
    }
  };

  return (
    <div
      className={`border-l-4 rounded-lg p-4 transition-all ${
        isResolved
          ? 'bg-gray-50 opacity-60'
          : `bg-white ${getSeverityColor(issue.severity)}`
      } hover:shadow-md cursor-pointer`}
    >
      <div onClick={onToggle}>
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1">
            {getSeverityIcon(issue.severity)}
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <h3 className={`font-semibold ${isResolved ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                  {issue.title}
                </h3>
                {issue.quick_win && (
                  <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full flex items-center">
                    <Zap className="w-3 h-3 mr-1" />
                    Quick Win
                  </span>
                )}
                <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${getCategoryColor(issue.category)}`}>
                  {issue.category}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{issue.description}</p>

              {/* Issue Metrics */}
              <div className="flex flex-wrap items-center gap-3 text-sm">
                <div className="flex items-center text-gray-600">
                  <span className="font-medium mr-1">Pages:</span>
                  <span>{issue.pages_affected}</span>
                </div>
                <div className="flex items-center text-green-600">
                  <span className="font-medium mr-1">Impact:</span>
                  <span>+{issue.impact} pts</span>
                </div>
                <div className="flex items-center">
                  {getEffortBadge(issue.effort)}
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 ml-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onMarkResolved();
              }}
              className={`p-2 rounded transition-colors ${
                isResolved
                  ? 'bg-green-100 text-green-600'
                  : 'bg-gray-100 text-gray-400 hover:bg-green-50 hover:text-green-600'
              }`}
              title={isResolved ? 'Mark as unresolved' : 'Mark as resolved'}
            >
              {isResolved ? <Check className="w-5 h-5" /> : <X className="w-5 h-5" />}
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Recommendation */}
        {!isExpanded && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">Quick fix:</span> {issue.recommendation}
            </p>
          </div>
        )}
      </div>

      {/* Expanded Details */}
      {isExpanded && issue.details && (
        <div className="mt-4 pt-4 border-t border-gray-300 animate-slide-down">
          <IssueDetails issue={issue} />
        </div>
      )}
    </div>
  );
}

// Issue Details Component
function IssueDetails({ issue }: { issue: Issue }) {
  return (
    <div className="space-y-4">
      {/* Full Explanation */}
      {issue.details?.explanation && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">📋 Technical Explanation</h4>
          <p className="text-sm text-gray-700 leading-relaxed">{issue.details.explanation}</p>
        </div>
      )}

      {/* Fix Steps */}
      {issue.details?.fix_steps && issue.details.fix_steps.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">🔧 How to Fix</h4>
          <ol className="list-decimal list-inside space-y-2">
            {issue.details.fix_steps.map((step, index) => (
              <li key={index} className="text-sm text-gray-700 leading-relaxed">
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Code Example */}
      {issue.details?.code_example && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">💻 Code Example</h4>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
            <code>{issue.details.code_example}</code>
          </pre>
        </div>
      )}

      {/* Recommendation */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">💡 Recommendation</h4>
        <p className="text-sm text-blue-800">{issue.recommendation}</p>
      </div>
    </div>
  );
}

// Helper Functions
function getEffortBadge(effort: Issue['effort']) {
  const badges = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800'
  };

  return (
    <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${badges[effort]}`}>
      {effort.charAt(0).toUpperCase() + effort.slice(1)} Effort
    </span>
  );
}

function getCategoryColor(category: Issue['category']) {
  const colors = {
    SEO: 'bg-purple-100 text-purple-800',
    AEO: 'bg-green-100 text-green-800',
    GEO: 'bg-orange-100 text-orange-800'
  };
  return colors[category];
}
