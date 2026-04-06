import type { Metadata } from 'next';
import { Navbar } from '@/components/Navbar';
import '../globals.css';

export const metadata: Metadata = {
  title: { default: 'MedFactCheck — AI Medical Claim Verification', template: '%s | MedFactCheck' },
  description: 'Verify medical claims from videos, text, and social media with AI-powered fact-checking. Supports Arabic, Darija, and English.',
  keywords: ['medical fact-checking', 'AI verification', 'Arabic', 'Darija', 'health misinformation'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body className="min-h-screen">
        <Navbar />
        <main className="min-h-[calc(100vh-64px)]">
          {children}
        </main>
        <footer className="border-t border-white/5 bg-[#0a0e1a]/80 py-8 mt-12">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-xs font-bold">MF</div>
              <span className="text-sm text-slate-400">MedFactCheck v1.0 — AI Medical Fact-Checking Platform</span>
            </div>
            <p className="text-xs text-slate-600">For educational and research purposes only.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
