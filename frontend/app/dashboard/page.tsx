'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('credisure_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('credisure_token');
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-blue-600">CrediSure</h1>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back!</h2>
          <p className="text-gray-600">
            Manage your credit profile and get funding ready.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-2">Credit Score</h3>
            <p className="text-4xl font-bold text-gray-900">—</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-2">Risk Rating</h3>
            <p className="text-2xl font-semibold text-gray-700">—</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-2">Funding Readiness</h3>
            <p className="text-2xl font-semibold text-gray-700">—</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <a
            href="/assessment"
            className="flex-1 bg-blue-600 text-white text-center py-4 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
          >
            Get Credit Assessment
          </a>
          <a
            href="/upload"
            className="flex-1 bg-white text-blue-600 text-center py-4 rounded-xl font-semibold border border-blue-600 hover:bg-blue-50 transition-colors"
          >
            Upload Bank Statement
          </a>
          <a
            href="/analysis"
            className="flex-1 bg-purple-600 text-white text-center py-4 rounded-xl font-semibold hover:bg-purple-700 transition-colors"
          >
            AI Statement Analysis
          </a>
        </div>
      </main>
    </div>
  );
}
