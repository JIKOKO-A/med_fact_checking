'use client';

import React, { useState } from 'react';
import { VerificationResult } from '@/services/api';

interface VerificationCardProps {
  result: VerificationResult;
  claimId?: number | string;
  transcription?: string;
}

const LABEL_CONFIG: Record<string, { badge: string; text: string; icon: string; border: string; glow: string }> = {
  true: {
    badge: 'badge-true',
    text: 'Verified True',
    icon: '✓',
    border: 'border-emerald-500/30',
    glow: 'shadow-emerald-500/10',
  },
  false: {
    badge: 'badge-false',
    text: 'Verified False',
    icon: '✗',
    border: 'border-red-500/30',
    glow: 'shadow-red-500/10',
  },
  partially_true: {
    badge: 'badge-partial',
    text: 'Partially True',
    icon: '⚠',
    border: 'border-yellow-500/30',
    glow: 'shadow-yellow-500/10',
  },
  unverifiable: {
    badge: 'badge-unverifiable',
    text: 'Unverifiable',
    icon: '?',
    border: 'border-slate-500/30',
    glow: 'shadow-slate-500/10',
  },
};

export const VerificationCard: React.FC<VerificationCardProps> = ({ result, claimId, transcription }) => {
  const [showDarija, setShowDarija] = useState(false);
  const [showTranscription, setShowTranscription] = useState(false);

  const cfg = LABEL_CONFIG[result.verification_label] || LABEL_CONFIG.unverifiable;
  const confidencePct = Math.round(result.confidence_score * 100);

  const confidenceColor =
    result.confidence_score >= 0.8 ? 'from-emerald-500 to-cyan-400' :
    result.confidence_score >= 0.5 ? 'from-yellow-500 to-amber-400' :
    'from-red-500 to-rose-400';

  return (
    <div className={`animate-fade-in-up glass-card p-6 border ${cfg.border} shadow-xl ${cfg.glow}`}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1">
          {claimId !== undefined && (
            <p className="text-xs text-slate-500 mb-1.5">
              Claim #{typeof claimId === 'number' ? claimId : claimId}
            </p>
          )}
          <h3 className="text-base font-semibold text-white leading-snug">
            {result.claim || result.original_text}
          </h3>
        </div>
        <span className={cfg.badge}>
          <span className="mr-1">{cfg.icon}</span>
          {cfg.text}
        </span>
      </div>

      {/* Confidence bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-xs text-slate-400">Confidence</span>
          <span className="text-sm font-bold text-white">{confidencePct}%</span>
        </div>
        <div className="confidence-bar">
          <div
            className={`confidence-bar-fill bg-gradient-to-r ${confidenceColor}`}
            style={{ width: `${confidencePct}%` }}
          />
        </div>
      </div>

      {/* Explanation */}
      {result.explanation && (
        <div className="mb-4 p-3 rounded-lg bg-white/3 border border-white/5">
          <p className="text-sm text-slate-300 leading-relaxed">{result.explanation}</p>
        </div>
      )}

      {/* Meta grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {result.claim_type && (
          <MetaChip label="Claim Type" value={result.claim_type} />
        )}
        {result.medical_domain && (
          <MetaChip label="Domain" value={result.medical_domain} />
        )}
        {result.processing_time_ms && (
          <MetaChip label="Processing" value={`${result.processing_time_ms.toFixed(0)}ms`} />
        )}
        {result.source_url && (
          <div className="col-span-2 md:col-span-3">
            <p className="text-xs text-slate-500 mb-0.5">Source</p>
            <a href={result.source_url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:text-blue-300 truncate block">
              {result.source_url}
            </a>
          </div>
        )}
      </div>

      {/* Darija translation toggle */}
      {(result.darija_latin || result.darija_arabic) && (
        <>
          <button
            onClick={() => setShowDarija(!showDarija)}
            className="w-full text-left text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors"
          >
            <span className="inline-block transition-transform" style={{ transform: showDarija ? 'rotate(90deg)' : 'none' }}>▶</span>
            Moroccan Darija Translation
          </button>
          {showDarija && (
            <div className="mt-2 p-3 rounded-lg bg-white/3 border border-white/5 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Latin Script</p>
                <p className="text-sm text-slate-300">{result.darija_latin}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Arabic Script</p>
                <p className="text-sm text-slate-300 text-right" dir="rtl">{result.darija_arabic}</p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

const MetaChip: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="bg-white/3 border border-white/5 rounded-lg px-3 py-2">
    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">{label}</p>
    <p className="text-xs font-medium text-slate-300 capitalize">{value.replace(/_/g, ' ')}</p>
  </div>
);
