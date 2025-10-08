"use client";

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Plus, X, AlertCircle, Loader2 } from 'lucide-react';
import { startComparison, isValidUrl, normalizeUrl } from '../lib/api';

export default function ComparisonInputForm() {
  const router = useRouter();

  // Form state
  const [userUrl, setUserUrl] = useState('');
  const [competitorUrls, setCompetitorUrls] = useState(['', '']);
  const [maxPages, setMaxPages] = useState(50);

  // Status state
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Add competitor input
  const addCompetitor = () => {
    if (competitorUrls.length < 3) {
      setCompetitorUrls([...competitorUrls, '']);
    }
  };

  // Remove competitor input
  const removeCompetitor = (index: number) => {
    if (competitorUrls.length > 1) {
      setCompetitorUrls(competitorUrls.filter((_, i) => i !== index));
    }
  };

  // Update competitor URL
  const updateCompetitor = (index: number, value: string) => {
    const updated = [...competitorUrls];
    updated[index] = value;
    setCompetitorUrls(updated);
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate user URL
    if (!userUrl.trim()) {
      newErrors.userUrl = 'Please enter your website URL';
    } else if (!isValidUrl(userUrl)) {
      newErrors.userUrl = 'Please enter a valid URL';
    }

    // Validate competitor URLs
    const validCompetitors = competitorUrls.filter(url => url.trim());
    if (validCompetitors.length === 0) {
      newErrors.competitors = 'Please enter at least one competitor URL';
    }

    competitorUrls.forEach((url, index) => {
      if (url.trim() && !isValidUrl(url)) {
        newErrors[`competitor${index}`] = 'Invalid URL';
      }
    });

    // Check for duplicates
    const allUrls = [userUrl, ...validCompetitors].map(u => normalizeUrl(u).toLowerCase());
    const uniqueUrls = new Set(allUrls);
    if (allUrls.length !== uniqueUrls.size) {
      newErrors.duplicates = 'URLs must be unique';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const validCompetitors = competitorUrls.filter(url => url.trim());

    try {
      setLoading(true);
      setErrors({});

      // Start the comparison
      const response = await startComparison(
        normalizeUrl(userUrl),
        validCompetitors.map(normalizeUrl),
        maxPages
      );

      // Navigate to results page
      router.push(`/compare/${response.comparison_id}`);
    } catch (error) {
      console.error('Failed to start comparison:', error);
      setErrors({ submit: error instanceof Error ? error.message : 'Failed to start comparison' });
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8 space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
            <Users className="w-6 h-6 mr-2 text-blue-600" />
            Competitor Comparison
          </h2>
          <p className="text-gray-600">
            Compare your website against up to 3 competitors to identify opportunities
          </p>
        </div>

        {/* User URL */}
        <div>
          <label htmlFor="userUrl" className="block text-sm font-medium text-gray-700 mb-2">
            Your Website URL
          </label>
          <input
            id="userUrl"
            type="text"
            value={userUrl}
            onChange={(e) => setUserUrl(e.target.value)}
            placeholder="example.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          {errors.userUrl && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.userUrl}
            </p>
          )}
        </div>

        {/* Competitor URLs */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Competitor URLs (1-3)
          </label>
          <div className="space-y-3">
            {competitorUrls.map((url, index) => (
              <div key={index} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => updateCompetitor(index, e.target.value)}
                  placeholder={`Competitor ${index + 1}`}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                />
                {competitorUrls.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeCompetitor(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    disabled={loading}
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            ))}
          </div>
          {competitorUrls.length < 3 && (
            <button
              type="button"
              onClick={addCompetitor}
              className="mt-3 flex items-center text-sm text-blue-600 hover:text-blue-700"
              disabled={loading}
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Competitor
            </button>
          )}
          {errors.competitors && (
            <p className="mt-2 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.competitors}
            </p>
          )}
          {errors.duplicates && (
            <p className="mt-2 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.duplicates}
            </p>
          )}
        </div>

        {/* Max Pages */}
        <div>
          <label htmlFor="maxPages" className="block text-sm font-medium text-gray-700 mb-2">
            Max Pages per Site
          </label>
          <input
            id="maxPages"
            type="number"
            min="10"
            max="100"
            value={maxPages}
            onChange={(e) => setMaxPages(Number(e.target.value))}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
        </div>

        {/* Error Messages */}
        {errors.submit && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800 flex items-center">
              <AlertCircle className="w-4 h-4 mr-2" />
              {errors.submit}
            </p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg font-semibold"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Starting Comparison...
            </>
          ) : (
            <>
              <Users className="w-5 h-5 mr-2" />
              Start Comparison
            </>
          )}
        </button>

        <p className="text-sm text-gray-500 text-center">
          Analysis takes ~1-2 minutes per site. You'll be redirected to the results page.
        </p>
      </div>
    </form>
  );
}
