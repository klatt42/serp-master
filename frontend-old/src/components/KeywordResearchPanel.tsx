import React, { useState } from 'react';
import axios from 'axios';

const KeywordResearchPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('United States');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleResearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/keywords/research', {
        query,
        location
      });
      setResults(response.data);
    } catch (error: any) {
      setResults({
        query,
        location,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">Keyword Research</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Query
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., SEO tools for small business"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && handleResearch()}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <select
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="United States">United States</option>
            <option value="United Kingdom">United Kingdom</option>
            <option value="Canada">Canada</option>
            <option value="Australia">Australia</option>
          </select>
        </div>

        <button
          onClick={handleResearch}
          disabled={loading || !query.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Researching...' : 'Research Keywords'}
        </button>

        {/* Results */}
        {results && (
          <div className="border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">
              Results for "{results.query}" in {results.location}
            </h3>

            {results.error ? (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-sm text-red-800">
                  Error: {results.error}
                </div>
              </div>
            ) : (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="text-sm text-blue-800">
                  <strong>API Response Received!</strong>
                  <pre className="mt-2 text-xs overflow-auto max-h-60">
                    {JSON.stringify(results.data, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default KeywordResearchPanel;
