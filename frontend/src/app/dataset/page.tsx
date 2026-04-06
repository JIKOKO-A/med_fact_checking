'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { apiClient, ClaimDataResponse, VerificationResult } from '@/services/api';

const DOMAINS = ['', 'general_medicine', 'cardiology', 'nutrition', 'vaccination', 'mental_health', 'oncology', 'pediatrics'];
const LABELS = ['', 'true', 'false', 'partially_true', 'unverifiable'];

const BADGE: Record<string, string> = {
  true: 'badge-true',
  false: 'badge-false',
  partially_true: 'badge-partial',
  unverifiable: 'badge-unverifiable',
};

export default function DatasetPage() {
  const [data, setData] = useState<ClaimDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(1);
  const [perPage] = useState(15);
  const [domain, setDomain] = useState('');
  const [label, setLabel] = useState('');
  const [minConf, setMinConf] = useState(0);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (domain) filters.domain = domain;
      if (label) filters.label = label;
      if (minConf > 0) filters.min_confidence = minConf / 100;
      const result = await apiClient.getDataset(page, perPage, filters);
      setData(result);
      setError(null);
    } catch {
      setError('Failed to load dataset. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, [page, perPage, domain, label, minConf]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const totalPages = data ? Math.ceil(data.total_count / perPage) : 0;

  const resetFilters = () => {
    setDomain('');
    setLabel('');
    setMinConf(0);
    setPage(1);
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="mb-8">
        <h1 className="section-title text-3xl mb-1">Claims Dataset</h1>
        <p className="text-slate-400 text-sm">Browse, filter, and explore all verified claims in the database</p>
      </div>

      {/* Filters */}
      <div className="glass-card p-5 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
          <div>
            <label htmlFor="filter-domain" className="block text-xs text-slate-400 mb-1">Medical Domain</label>
            <select
              id="filter-domain"
              value={domain}
              onChange={(e) => { setDomain(e.target.value); setPage(1); }}
              className="glass-input w-full px-3 py-2 text-sm"
            >
              <option value="" className="bg-[#0f1629]">All Domains</option>
              {DOMAINS.filter(Boolean).map((d) => (
                <option key={d} value={d} className="bg-[#0f1629] capitalize">{d.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="filter-label" className="block text-xs text-slate-400 mb-1">Verdict</label>
            <select
              id="filter-label"
              value={label}
              onChange={(e) => { setLabel(e.target.value); setPage(1); }}
              className="glass-input w-full px-3 py-2 text-sm"
            >
              <option value="" className="bg-[#0f1629]">All Verdicts</option>
              {LABELS.filter(Boolean).map((l) => (
                <option key={l} value={l} className="bg-[#0f1629] capitalize">{l.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="filter-confidence" className="block text-xs text-slate-400 mb-1">
              Min Confidence: <span className="text-white font-semibold">{minConf}%</span>
            </label>
            <input
              id="filter-confidence"
              type="range"
              min={0}
              max={100}
              step={5}
              value={minConf}
              onChange={(e) => { setMinConf(Number(e.target.value)); setPage(1); }}
              className="w-full accent-blue-500"
            />
          </div>

          <button
            id="reset-filters"
            onClick={resetFilters}
            className="btn-ghost text-sm py-2"
          >
            ↺ Reset Filters
          </button>
        </div>

        {/* Active filters */}
        {(domain || label || minConf > 0) && (
          <div className="mt-3 flex flex-wrap gap-2">
            {domain && <FilterTag label={`Domain: ${domain}`} onRemove={() => setDomain('')} />}
            {label && <FilterTag label={`Verdict: ${label}`} onRemove={() => setLabel('')} />}
            {minConf > 0 && <FilterTag label={`Confidence ≥ ${minConf}%`} onRemove={() => setMinConf(0)} />}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 mb-6 rounded-xl bg-red-500/10 border border-red-500/20">
          <p className="text-red-400 text-sm">❌ {error}</p>
        </div>
      )}

      {/* Count */}
      {data && (
        <p className="text-sm text-slate-400 mb-4">
          Showing {(page - 1) * perPage + 1}–{Math.min(page * perPage, data.total_count)} of <span className="text-white font-semibold">{data.total_count}</span> claims
        </p>
      )}

      {/* Loading */}
      {loading && (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-16 rounded-xl" />
          ))}
        </div>
      )}

      {/* Table */}
      {data && !loading && (
        <div className="glass-card overflow-hidden mb-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 uppercase tracking-wider border-b border-white/5">
                  <th className="text-left px-5 py-3">Claim</th>
                  <th className="text-left px-5 py-3 hidden lg:table-cell">Type</th>
                  <th className="text-left px-5 py-3 hidden md:table-cell">Domain</th>
                  <th className="text-left px-5 py-3">Verdict</th>
                  <th className="text-right px-5 py-3">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {data.claims.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-12 text-center text-slate-500">
                      No claims found matching your filters.
                    </td>
                  </tr>
                ) : (
                  data.claims.map((claim, i) => (
                    <tr
                      key={i}
                      className="border-b border-white/5 hover:bg-white/3 transition-colors"
                    >
                      <td className="px-5 py-3">
                        <div>
                          <p className="text-slate-200 font-medium truncate max-w-xs" title={claim.claim}>
                            {claim.claim || claim.original_text}
                          </p>
                          <p className="text-xs text-slate-500 truncate max-w-xs mt-0.5" dir="rtl" title={claim.original_text}>
                            {claim.original_text !== claim.claim ? claim.original_text : ''}
                          </p>
                        </div>
                      </td>
                      <td className="px-5 py-3 hidden lg:table-cell">
                        <span className="text-xs text-slate-400 capitalize">{(claim.claim_type || '').replace(/_/g, ' ')}</span>
                      </td>
                      <td className="px-5 py-3 hidden md:table-cell">
                        <span className="text-xs text-slate-400 capitalize">{(claim.medical_domain || '').replace(/_/g, ' ')}</span>
                      </td>
                      <td className="px-5 py-3">
                        <span className={BADGE[claim.verification_label] || 'badge-unverifiable'}>
                          {claim.verification_label?.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-16 confidence-bar hidden sm:block">
                            <div
                              className="confidence-bar-fill"
                              style={{ width: `${(claim.confidence_score * 100).toFixed(0)}%` }}
                            />
                          </div>
                          <span className="text-white font-semibold text-xs">{((claim.confidence_score || 0) * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-2">
          <button
            id="pagination-prev"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="btn-ghost px-4 py-2 text-sm disabled:opacity-40"
          >
            ← Prev
          </button>
          <div className="flex gap-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const p = Math.max(1, Math.min(page - 2, totalPages - 4)) + i;
              return (
                <button
                  key={p}
                  id={`page-btn-${p}`}
                  onClick={() => setPage(p)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                    p === page ? 'bg-blue-500 text-white' : 'text-slate-400 hover:bg-white/10'
                  }`}
                >
                  {p}
                </button>
              );
            })}
          </div>
          <button
            id="pagination-next"
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="btn-ghost px-4 py-2 text-sm disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}

const FilterTag: React.FC<{ label: string; onRemove: () => void }> = ({ label, onRemove }) => (
  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs text-blue-400">
    {label}
    <button onClick={onRemove} className="hover:text-white transition-colors">✕</button>
  </span>
);
