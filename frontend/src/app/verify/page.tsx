'use client';

import React, { useState } from 'react';
import { apiClient, VerifyResponse, VideoProcessingResponse, VerificationResult } from '@/services/api';
import { VerificationCard } from '@/components/VerificationCard';

type Mode = 'video' | 'text' | 'batch';
type Language = 'ar' | 'en' | 'fr';

const TABS: { id: Mode; label: string; icon: string; primary?: boolean }[] = [
  { id: 'video', label: 'Video URL', icon: '🎬', primary: true },
  { id: 'text', label: 'Text Claim', icon: '📝' },
  { id: 'batch', label: 'Batch (up to 10)', icon: '📦' },
];

const LANG_OPTIONS: { value: Language; label: string }[] = [
  { value: 'ar', label: 'Arabic / Darija (العربية)' },
  { value: 'en', label: 'English' },
  { value: 'fr', label: 'French (Français)' },
];

export default function VerifyPage() {
  const [mode, setMode] = useState<Mode>('video');
  const [text, setText] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [batchTexts, setBatchTexts] = useState<string[]>(['', '']);
  const [language, setLanguage] = useState<Language>('ar');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');

  // Results
  const [textResult, setTextResult] = useState<VerifyResponse | null>(null);
  const [videoResult, setVideoResult] = useState<VideoProcessingResponse | null>(null);
  const [batchResults, setBatchResults] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const clearResults = () => {
    setTextResult(null);
    setVideoResult(null);
    setBatchResults(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    clearResults();

    try {
      if (mode === 'video') {
        setProgress('⬇️ Downloading audio from video...');
        const res = await apiClient.verifyVideoUrl(videoUrl, language);
        setProgress('');
        setVideoResult(res);
        if (!res.success && res.error) setError(res.error);
      } else if (mode === 'text') {
        setProgress('🔍 Verifying claim...');
        const res = await apiClient.verify(text, language);
        setProgress('');
        setTextResult(res);
      } else {
        // batch
        const filled = batchTexts.filter((t) => t.trim().length >= 10);
        if (filled.length === 0) {
          setError('Please enter at least one claim (min 10 characters each).');
          setLoading(false);
          return;
        }
        setProgress(`🔄 Verifying ${filled.length} claim(s)...`);
        const res = await apiClient.verifyBatch(filled, language);
        setProgress('');
        setBatchResults(res.results || []);
      }
    } catch (err: any) {
      setProgress('');
      const msg = err?.response?.data?.detail || err?.message || 'Verification failed. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const canSubmit =
    !loading &&
    (mode === 'video' ? videoUrl.trim().length > 0
     : mode === 'text' ? text.trim().length >= 10
     : batchTexts.some((t) => t.trim().length >= 10));

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="mb-8 text-center">
        <h1 className="section-title text-4xl mb-2">Claim Verifier</h1>
        <p className="text-slate-400">
          Paste a <strong className="text-blue-400">video URL</strong> to automatically extract and verify all medical claims, or enter text directly.
        </p>
      </div>

      {/* Mode Tabs */}
      <div className="glass-card p-1 flex gap-1 mb-6 max-w-xl mx-auto">
        {TABS.map(({ id, label, icon, primary }) => (
          <button
            key={id}
            id={`tab-${id}`}
            onClick={() => { setMode(id); clearResults(); }}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-sm font-medium transition-all duration-200 ${
              mode === id
                ? primary
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/25'
                  : 'bg-white/10 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
            }`}
          >
            <span>{icon}</span>
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>

      {/* Form */}
      <div className="glass-card max-w-2xl mx-auto p-7 mb-8">
        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Video Mode */}
          {mode === 'video' && (
            <div>
              <label htmlFor="videoUrl" className="block text-sm font-medium text-slate-300 mb-2">
                Video URL <span className="text-blue-400">*</span>
              </label>
              <input
                id="videoUrl"
                type="url"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=...  or TikTok / Facebook / Instagram"
                className="glass-input w-full px-4 py-3 text-sm"
                required
              />
              <p className="mt-2 text-xs text-slate-500">
                ⏱ Max 5 minutes. Supported: YouTube, TikTok, Facebook, Instagram, Twitter.
              </p>

              {/* Supported platforms */}
              <div className="mt-3 flex flex-wrap gap-2">
                {['YouTube', 'TikTok', 'Facebook', 'Instagram', 'Twitter'].map((p) => (
                  <span key={p} className="px-2.5 py-1 rounded-full bg-white/5 border border-white/8 text-xs text-slate-400">
                    {p}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Text Mode */}
          {mode === 'text' && (
            <div>
              <label htmlFor="claimText" className="block text-sm font-medium text-slate-300 mb-2">
                Medical Claim <span className="text-blue-400">*</span>
              </label>
              <textarea
                id="claimText"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter a medical claim in Arabic, Darija, or English…"
                rows={5}
                className="glass-input w-full px-4 py-3 text-sm resize-none"
              />
              <p className="mt-1 text-xs text-slate-500">
                {text.length} / 5000 characters {text.length < 10 && text.length > 0 && '(min 10)'}
              </p>
            </div>
          )}

          {/* Batch Mode */}
          {mode === 'batch' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-slate-300">Claims (min 10 chars each)</label>
                <span className="text-xs text-slate-500">{batchTexts.filter(t => t.trim().length >= 10).length} / {batchTexts.length} valid</span>
              </div>
              <div className="space-y-2">
                {batchTexts.map((t, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="flex-shrink-0 w-6 h-10 flex items-center justify-center text-xs text-slate-500">{i + 1}</span>
                    <input
                      id={`batch-claim-${i}`}
                      type="text"
                      value={t}
                      onChange={(e) => {
                        const next = [...batchTexts];
                        next[i] = e.target.value;
                        setBatchTexts(next);
                      }}
                      placeholder={`Claim ${i + 1}…`}
                      className="glass-input flex-1 px-3 py-2.5 text-sm"
                    />
                    {batchTexts.length > 2 && (
                      <button
                        type="button"
                        onClick={() => setBatchTexts(batchTexts.filter((_, j) => j !== i))}
                        className="text-slate-500 hover:text-red-400 transition-colors text-sm px-1"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>
              {batchTexts.length < 10 && (
                <button
                  type="button"
                  onClick={() => setBatchTexts([...batchTexts, ''])}
                  className="mt-3 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                  id="add-batch-claim"
                >
                  + Add another claim
                </button>
              )}
            </div>
          )}

          {/* Language selector */}
          <div>
            <label htmlFor="language" className="block text-sm font-medium text-slate-300 mb-2">Language</label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
              className="glass-input w-full px-4 py-2.5 text-sm"
            >
              {LANG_OPTIONS.map(({ value, label }) => (
                <option key={value} value={value} className="bg-[#0f1629]">{label}</option>
              ))}
            </select>
          </div>

          {/* Submit */}
          <button
            id="submit-verify"
            type="submit"
            disabled={!canSubmit}
            className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 text-base"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                {progress || 'Processing…'}
              </>
            ) : mode === 'video' ? (
              <><span>🎬</span> Analyze Video URL</>
            ) : mode === 'batch' ? (
              <><span>📦</span> Verify All Claims</>
            ) : (
              <><span>🔍</span> Verify Claim</>
            )}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="max-w-2xl mx-auto mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 animate-fade-in">
          <p className="text-red-400 text-sm">❌ {error}</p>
        </div>
      )}

      {/* Premium Video Results Workbench */}
      {videoResult && videoResult.success && (
        <div className="max-w-5xl mx-auto animate-fade-in-up mt-8">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
            <h2 className="text-2xl font-bold text-white flex items-center gap-3">
              <span className="p-2 rounded-lg bg-blue-500/20 text-blue-400">🎬</span>
              Video Analysis Studio
            </h2>
            <span className="badge-true flex items-center gap-1.5 px-3 py-1.5 text-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Processing Complete
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Native Transcription Panel */}
            <div className="glass-card shadow-lg shadow-blue-900/10 border border-white/5 overflow-hidden flex flex-col">
              <div className="bg-white/5 border-b border-white/5 px-5 py-3 flex items-center justify-between">
                <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center gap-2">
                  <span className="text-blue-400">📄</span> Source Transcription
                </p>
                <span className="text-[10px] px-2 py-0.5 rounded-md bg-white/10 text-slate-400">
                  {language === 'ar' ? 'Darija / Arabic' : language.toUpperCase()}
                </span>
              </div>
              <div className="p-5 flex-1 relative bg-[#0a0f1c]/50">
                <p className="text-sm text-slate-300 leading-relaxed font-arabic" dir={language === 'ar' ? 'rtl' : 'ltr'}>
                  {videoResult.transcription || "No speech detected in the provided video."}
                </p>
              </div>
            </div>

            {/* English Translation Panel */}
            <div className="glass-card shadow-lg shadow-cyan-900/10 border border-white/5 overflow-hidden flex flex-col relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 pointer-events-none" />
              <div className="bg-white/5 border-b border-white/5 px-5 py-3 flex items-center justify-between relative z-10">
                <p className="text-xs font-semibold text-white uppercase tracking-widest flex items-center gap-2">
                  <span className="text-cyan-400">🌍</span> English Translation
                </p>
                <span className="text-[10px] px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  AI Translated
                </span>
              </div>
              <div className="p-5 flex-1 relative z-10 bg-[#0a0f1c]/30">
                <p className="text-sm text-slate-200 leading-relaxed">
                  {videoResult.english_translation || (videoResult.transcription ? "Translation processing..." : "No text available for translation.")}
                </p>
              </div>
            </div>
          </div>

          {/* Verified Claims Section */}
          <div className="mt-8 pt-8 border-t border-white/5">
            <h3 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
              <span className="text-amber-400">🔍</span> Extracted Medical Claims
            </h3>
            {videoResult.verification_results && videoResult.verification_results.length > 0 ? (
              <div className="grid grid-cols-1 gap-4">
                {videoResult.verification_results.map((res, i) => (
                  <VerificationCard
                    key={i}
                    result={res}
                    claimId={i + 1}
                  />
                ))}
              </div>
            ) : (
              <div className="glass-card p-8 text-center border border-yellow-500/20 bg-yellow-500/5">
                <p className="text-2xl mb-3">🔎</p>
                <p className="text-slate-300 font-medium mb-1">No actionable medical claims detected</p>
                <p className="text-sm text-slate-500 max-w-md mx-auto">
                  The transcribed text did not contain verifiable medical claims or health-related statements.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Text Result */}
      {textResult && (
        <div className="max-w-2xl mx-auto animate-fade-in-up">
          <h2 className="text-xl font-bold text-white mb-4">Verification Result</h2>
          <VerificationCard result={textResult.data} claimId={textResult.claim_id} />
        </div>
      )}

      {/* Batch Results */}
      {batchResults && (
        <div className="max-w-3xl mx-auto animate-fade-in-up">
          <div className="flex items-center gap-3 mb-5">
            <h2 className="text-xl font-bold text-white">Batch Results</h2>
            <span className="text-xs text-slate-400">{batchResults.length} claims verified</span>
          </div>
          <div className="space-y-4">
            {batchResults.map((res: any, i: number) => (
              <VerificationCard key={i} result={res.data || res} claimId={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
