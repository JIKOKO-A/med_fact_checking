'use client';

import React, { useEffect, useState } from 'react';
import { apiClient, AnalyticsData, TrendingClaim, ConfidenceDistribution } from '@/services/api';
import { AnalyticsDashboard } from '@/components/AnalyticsDashboard';
import type { Metadata } from 'next';

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [trending, setTrending] = useState<TrendingClaim[]>([]);
  const [confDist, setConfDist] = useState<ConfidenceDistribution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);

  const LABEL_BADGE: Record<string, string> = {
    true: 'badge-true',
    false: 'badge-false',
    partially_true: 'badge-partial',
    unverifiable: 'badge-unverifiable',
  };

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setLoading(true);
        const [analyticsData, trendingData, distData] = await Promise.all([
          apiClient.getDashboardAnalytics(days),
          apiClient.getTrendingClaims(10),
          apiClient.getConfidenceDistribution(days),
        ]);
        setAnalytics(analyticsData);
        setTrending(trendingData);
        setConfDist(distData);
        setError(null);
      } catch (err: any) {
        setError('Failed to load analytics. Make sure the backend is running.');
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [days]);

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="section-title text-3xl mb-1">Analytics Dashboard</h1>
          <p className="text-slate-400 text-sm">Real-time fact-checking insights & metrics</p>
        </div>
        <select
          id="days-filter"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="glass-input px-4 py-2 text-sm w-full sm:w-auto"
        >
          <option value={1} className="bg-[#0f1629]">Last 24 Hours</option>
          <option value={7} className="bg-[#0f1629]">Last 7 Days</option>
          <option value={30} className="bg-[#0f1629]">Last 30 Days</option>
          <option value={90} className="bg-[#0f1629]">Last 90 Days</option>
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 mb-6 rounded-xl bg-red-500/10 border border-red-500/20 animate-fade-in">
          <p className="text-red-400 text-sm">❌ {error}</p>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton h-24 rounded-xl" />
            ))}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="skeleton h-64 rounded-xl" />
            <div className="skeleton h-64 rounded-xl" />
          </div>
        </div>
      )}

      {/* Analytics */}
      {analytics && !loading && (
        <AnalyticsDashboard analytics={analytics} confidenceDistribution={confDist} />
      )}

      {/* Trending claims table */}
      {trending.length > 0 && !loading && (
        <div className="mt-8 glass-card overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5">
            <h2 className="text-base font-semibold text-white">🔥 Recently Verified Claims</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 uppercase tracking-wider border-b border-white/5">
                  <th className="text-left px-6 py-3">Claim</th>
                  <th className="text-left px-6 py-3 hidden md:table-cell">Domain</th>
                  <th className="text-left px-6 py-3">Verdict</th>
                  <th className="text-right px-6 py-3">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {trending.map((item, i) => (
                  <tr key={item.id} className={`border-b border-white/5 hover:bg-white/3 transition-colors ${i % 2 === 0 ? '' : 'bg-white/1'}`}>
                    <td className="px-6 py-3">
                      <p className="text-slate-300 truncate max-w-xs">{item.claim}</p>
                    </td>
                    <td className="px-6 py-3 hidden md:table-cell">
                      <span className="text-slate-400 text-xs capitalize">{(item.domain || '').replace(/_/g, ' ')}</span>
                    </td>
                    <td className="px-6 py-3">
                      <span className={LABEL_BADGE[item.label] || 'badge-unverifiable'}>
                        {item.label?.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-right">
                      <span className="text-white font-semibold">{((item.confidence || 0) * 100).toFixed(0)}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
