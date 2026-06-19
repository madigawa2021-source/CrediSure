'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AssessmentResult {
  credit_score: number;
  rating: string;
  risk_level: string;
}

export default function AssessmentPage() {
  const [monthlyIncome, setMonthlyIncome] = useState('');
  const [monthlyExpenses, setMonthlyExpenses] = useState('');
  const [existingLoans, setExistingLoans] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('credisure_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const getResultColor = (score: number) => {
    if (score >= 650) return 'bg-green-50 border-green-200';
    if (score >= 450) return 'bg-amber-50 border-amber-200';
    return 'bg-red-50 border-red-200';
  };

  const getTextColor = (score: number) => {
    if (score >= 650) return 'text-green-700';
    if (score >= 450) return 'text-amber-700';
    return 'text-red-700';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    const token = localStorage.getItem('credisure_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/assessment/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          monthly_income: parseFloat(monthlyIncome),
          monthly_expense: parseFloat(monthlyExpenses),
          existing_loans: parseFloat(existingLoans),
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Assessment failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center">
            <a href="/dashboard" className="text-gray-600 hover:text-gray-900 font-medium flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </a>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Credit Assessment</h2>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {result && (
          <div className={`mb-8 rounded-2xl p-8 border ${getResultColor(result.credit_score)}`}>
            <div className="text-center">
              <p className={`text-6xl font-bold mb-2 ${getTextColor(result.credit_score)}`}>
                {result.credit_score}
              </p>
              <p className={`text-2xl font-semibold mb-1 ${getTextColor(result.credit_score)}`}>
                {result.rating}
              </p>
              <p className={`text-lg ${getTextColor(result.credit_score)}`}>
                {result.risk_level}
              </p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border p-8 space-y-6">
          <div>
            <label htmlFor="monthlyIncome" className="block text-sm font-medium text-gray-700 mb-2">
              Monthly Income (₦)
            </label>
            <input
              id="monthlyIncome"
              type="number"
              value={monthlyIncome}
              onChange={(e) => setMonthlyIncome(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="500000"
            />
          </div>
          <div>
            <label htmlFor="monthlyExpenses" className="block text-sm font-medium text-gray-700 mb-2">
              Monthly Expenses (₦)
            </label>
            <input
              id="monthlyExpenses"
              type="number"
              value={monthlyExpenses}
              onChange={(e) => setMonthlyExpenses(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="200000"
            />
          </div>
          <div>
            <label htmlFor="existingLoans" className="block text-sm font-medium text-gray-700 mb-2">
              Existing Loans (₦)
            </label>
            <input
              id="existingLoans"
              type="number"
              value={existingLoans}
              onChange={(e) => setExistingLoans(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="50000"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Calculating...' : 'Calculate Score'}
          </button>
        </form>
      </main>
    </div>
  );
}
