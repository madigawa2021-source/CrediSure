
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type AssessmentResponse = {
  credit_score: number | null;
  rating: string | null;
  risk_level: string | null;
  assessed_at: string | null;
};

export default function DashboardPage() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [creditScore, setCreditScore] = useState<number | null>(null);
  const [riskRating, setRiskRating] = useState('Not assessed yet');
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('credisure_token');

    if (!token) {
      router.push('/login');
      return;
    }

    const storedEmail = localStorage.getItem('credisure_email');

    if (storedEmail) {
      setEmail(storedEmail);
    }

    const savedTheme = localStorage.getItem('darkMode') === 'true';

setDarkMode(savedTheme);

if (savedTheme) {
  document.documentElement.classList.add('dark');
}

    fetchLatestAssessment(token);
  }, [router]);

  const fetchLatestAssessment = async (token: string) => {
    try {
      const response = await fetch(
        `${API_URL}/assessment/latest`,
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data: AssessmentResponse = await response.json();

        setCreditScore(data.credit_score);
        setRiskRating(data.rating || 'Not assessed yet');
      } else if (response.status === 401) {
        localStorage.removeItem('credisure_token');
        localStorage.removeItem('credisure_email');

        router.push('/login');
      }
    } catch (error) {
      console.error('Failed to fetch assessment:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDarkMode = () => {
  const next = !darkMode;

  setDarkMode(next);

  localStorage.setItem('darkMode', String(next));

  document.documentElement.classList.toggle('dark', next);
  };

  const handleLogout = () => {
    localStorage.removeItem('credisure_token');
    localStorage.removeItem('credisure_email');

    router.push('/login');
  };

  const getFundingReadiness = () => {
    if (creditScore === null) {
      return {
        text: 'Not assessed yet',
        color: 'text-gray-700',
      };
    }

    if (creditScore >= 650) {
      return {
        text: 'Ready for Funding',
        color: 'text-green-600',
      };
    }

    if (creditScore >= 500) {
      return {
        text: 'Needs Improvement',
        color: 'text-amber-600',
      };
    }

    return {
      text: 'Not Ready',
      color: 'text-red-600',
    };
  };

  const funding = getFundingReadiness();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
  <h1 className="text-2xl font-bold text-blue-600">
    CrediSure
  </h1>

  <div className="flex items-center gap-3">
    <button
      onClick={toggleDarkMode}
      className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium"
    >
      {darkMode ? '☀️ Light' : '🌙 Dark'}
    </button>

    <button
      onClick={handleLogout}
      className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium"
    >
      Logout
    </button>
  </div>
</div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome Back!
          </h2>

          {email && (
            <p className="text-gray-600 dark:text-gray-300 mb-2">
              Signed in as: {email}
            </p>
          )}

          <p className="text-gray-600 dark:text-gray-300">
            Upload a bank statement to generate an AI-powered
            credit assessment and track your funding readiness.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-2">
              Credit Score
            </h3>

            <p className="text-4xl font-bold text-gray-900 dark:text-white">
              {loading
                ? 'Loading...'
                : creditScore !== null
                ? creditScore
                : 'Not assessed yet'}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-2">
              Risk Rating
            </h3>

            <p className="text-2xl font-semibold text-gray-700">
              {loading ? 'Loading...' : riskRating}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-2">
              Funding Readiness
            </h3>

            <p className={`text-2xl font-semibold ${funding.color}`}>
              {loading ? 'Loading...' : funding.text}
            </p>
          </div>
        </div>

  <div className="flex flex-col sm:flex-row gap-4">
    <a
      href="/analysis"
      className="flex-1 bg-blue-600 text-white text-center py-4 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
    >
      Upload a PDF Bank Statement
  </a>
  </div>
      </main>
    </div>
  );
}
