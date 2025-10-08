"use client";

import ComparisonInputForm from '../components/ComparisonInputForm';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ComparePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-8"
        >
          <ArrowLeft className="w-5 h-5 mr-1" />
          Back to Home
        </Link>

        {/* Form */}
        <ComparisonInputForm />
      </div>
    </div>
  );
}
