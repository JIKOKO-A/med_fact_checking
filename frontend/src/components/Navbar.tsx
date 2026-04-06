'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React, { useState, useEffect } from 'react';
import { apiClient } from '@/services/api';

const NAV_ITEMS = [
  { href: '/', label: 'Home', icon: '🏠' },
  { href: '/verify', label: 'Verify Video / Claim', icon: '🎬', highlight: true },
  { href: '/dashboard', label: 'Analytics', icon: '📊' },
  { href: '/dataset', label: 'Dataset', icon: '🗄️' },
  { href: '/status', label: 'System Status', icon: '💚' },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [health, setHealth] = useState<'healthy' | 'degraded' | 'unhealthy'>('healthy');

  useEffect(() => {
    apiClient.healthCheck().then((h) => setHealth(h.status as any));
  }, []);

  const statusColor =
    health === 'healthy' ? 'bg-emerald-400' :
    health === 'degraded' ? 'bg-yellow-400' : 'bg-red-400';

  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-[#0a0e1a]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-sm font-bold shadow-lg shadow-blue-500/30">
              MF
            </div>
            <span className="text-base font-bold text-white group-hover:text-blue-400 transition-colors">
              MedFactCheck
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(({ href, label, icon, highlight }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`nav-link ${active ? 'active' : ''} ${
                    highlight && !active
                      ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500/20'
                      : ''
                  }`}
                >
                  <span>{icon}</span>
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Status pill */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/8">
            <span className={`w-2 h-2 rounded-full ${statusColor} ${health === 'healthy' ? 'animate-pulse' : ''}`} />
            <span className="text-xs text-slate-400 capitalize">{health}</span>
          </div>

          {/* Mobile burger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5"
            aria-label="Menu"
          >
            {mobileOpen ? '✕' : '☰'}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileOpen && (
          <nav className="md:hidden py-3 border-t border-white/5 flex flex-col gap-1">
            {NAV_ITEMS.map(({ href, label, icon, highlight }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setMobileOpen(false)}
                  className={`nav-link ${active ? 'active' : ''} ${
                    highlight && !active ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : ''
                  }`}
                >
                  <span>{icon}</span>
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>
        )}
      </div>
    </header>
  );
}
