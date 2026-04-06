import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'MedFactCheck — AI Medical Claim Verification from Videos',
  description: 'Paste any video URL and instantly verify the medical claims inside. AI-powered, Arabic-first, real-time fact-checking.',
};

const FEATURES = [
  {
    icon: '🎬',
    title: 'Video URL Analysis',
    description: 'Paste a YouTube, TikTok, or Facebook video URL. We extract audio, transcribe speech, and verify every medical claim automatically.',
    highlight: true,
  },
  {
    icon: '🔍',
    title: 'Text Claim Verification',
    description: 'Paste any medical claim in Arabic, Darija, or English and get an instant AI-powered verdict.',
  },
  {
    icon: '📦',
    title: 'Batch Processing',
    description: 'Verify up to 10 claims at once. Perfect for researchers and content reviewers.',
  },
  {
    icon: '🌐',
    title: 'Moroccan Darija Support',
    description: 'Native Arabic & Latin Darija translation included in every result.',
  },
  {
    icon: '📊',
    title: 'Analytics Dashboard',
    description: 'Real-time misinformation rates, domain distributions, and daily trends.',
  },
  {
    icon: '💚',
    title: 'System Health Monitor',
    description: 'Live status of all platform services — database, cache, and ML engine.',
  },
];

const STEPS = [
  { step: '1', title: 'Paste a video URL', desc: 'YouTube, TikTok, Facebook, Instagram — any public video.' },
  { step: '2', title: 'AI extracts audio & transcribes', desc: 'We download audio and run speech-to-text transcription.' },
  { step: '3', title: 'Claims are verified', desc: 'Each medical claim is cross-checked against trusted sources.' },
  { step: '4', title: 'Get your results', desc: 'Full report with confidence scores, labels, and explanations.' },
];

export default function HomePage() {
  return (
    <div className="relative overflow-x-hidden">
      {/* ── HERO ─────────────────────────────────── */}
      <section className="relative py-24 px-6 text-center">
        {/* Ambient glows */}
        <div className="absolute inset-0 pointer-events-none" aria-hidden>
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-blue-600/10 rounded-full blur-[100px]" />
          <div className="absolute top-1/3 left-1/3 w-[400px] h-[200px] bg-cyan-500/8 rounded-full blur-[80px]" />
        </div>

        <div className="relative max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            AI-Powered Medical Fact-Checking
          </div>

          <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-6 leading-tight">
            <span className="text-white">Verify medical claims</span>
            <br />
            <span className="hero-gradient-text">from any video</span>
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Paste a social media video URL. Our AI downloads the audio, transcribes it, extracts medical claims, and returns instant fact-check results — in Arabic, Darija, or English.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/verify"
              className="btn-primary flex items-center gap-2 text-base px-8 py-3.5"
              id="hero-cta-verify"
            >
              <span>🎬</span> Analyze a Video URL
            </Link>
            <Link
              href="/dashboard"
              className="btn-ghost flex items-center gap-2 text-base px-8 py-3.5"
              id="hero-cta-dashboard"
            >
              <span>📊</span> View Analytics
            </Link>
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-center text-3xl font-bold text-white mb-3">How It Works</h2>
          <p className="text-center text-slate-400 mb-12">Four steps from video URL to verified claims</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {STEPS.map(({ step, title, desc }) => (
              <div key={step} className="glass-card p-5 text-center group hover:border-blue-500/30 transition-all">
                <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-xl font-black text-white shadow-lg shadow-blue-500/30">
                  {step}
                </div>
                <h3 className="font-semibold text-white mb-2">{title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES GRID ─────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-center text-3xl font-bold text-white mb-3">Platform Features</h2>
          <p className="text-center text-slate-400 mb-12">Everything you need to fight health misinformation</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map(({ icon, title, description, highlight }) => (
              <div
                key={title}
                className={`glass-card p-6 transition-all duration-300 ${
                  highlight
                    ? 'border-blue-500/30 shadow-blue-500/10 shadow-lg'
                    : ''
                }`}
              >
                {highlight && (
                  <span className="inline-block text-xs font-semibold text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-full mb-3">
                    Primary Feature
                  </span>
                )}
                <div className="text-3xl mb-3">{icon}</div>
                <h3 className="text-base font-semibold text-white mb-2">{title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ───────────────────────────── */}
      <section className="py-16 px-6">
        <div className="max-w-3xl mx-auto text-center glass-card p-12 gradient-border">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to fact-check a video?</h2>
          <p className="text-slate-400 mb-8">Paste any public social media video URL and get results in seconds.</p>
          <Link href="/verify" className="btn-primary inline-flex items-center gap-2 text-base px-10 py-4" id="bottom-cta-verify">
            <span>🎬</span> Start Now — It's Free
          </Link>
        </div>
      </section>
    </div>
  );
}
