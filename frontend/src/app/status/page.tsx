'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { apiClient, HealthStatus } from '@/services/api';
import { SystemStatusPanel } from '@/components/StatusCard';

export default function StatusPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [latency, setLatency] = useState<number | undefined>(undefined);
  const [ready, setReady] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkStatus = useCallback(async () => {
    setLoading(true);
    try {
      const [healthData, latencyData, readinessData] = await Promise.all([
        apiClient.healthCheck(),
        apiClient.getApiLatency(),
        apiClient.readinessCheck(),
      ]);
      setHealth(healthData);
      setLatency(latencyData.latency_ms);
      setReady(readinessData.ready);
      setLastChecked(new Date());
    } catch {
      setHealth({ status: 'unhealthy', database: 'unknown', redis: 'unknown', ml_service: 'unknown', version: 'N/A' });
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, [checkStatus]);

  const overallColor =
    health?.status === 'healthy' ? 'text-emerald-400' :
    health?.status === 'degraded' ? 'text-yellow-400' : 'text-red-400';

  const overallBg =
    health?.status === 'healthy' ? 'from-emerald-500/10 to-cyan-500/5 border-emerald-500/20' :
    health?.status === 'degraded' ? 'from-yellow-500/10 to-amber-500/5 border-yellow-500/20' :
    'from-red-500/10 to-rose-500/5 border-red-500/20';

  return (
    <div className="page-container max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="section-title text-3xl mb-1">System Status</h1>
          <p className="text-slate-400 text-sm">Live health monitoring — auto-refreshes every 30s</p>
        </div>
        <button
          id="refresh-status"
          onClick={checkStatus}
          disabled={loading}
          className="btn-ghost px-4 py-2 text-sm flex items-center gap-2"
        >
          {loading ? (
            <span className="w-4 h-4 rounded-full border-2 border-slate-600 border-t-slate-300 animate-spin" />
          ) : (
            <span>↺</span>
          )}
          Refresh
        </button>
      </div>

      {/* Overall status banner */}
      {health && (
        <div className={`mb-6 p-5 rounded-xl bg-gradient-to-r border ${overallBg} animate-fade-in`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">
                {health.status === 'healthy' ? '✅' : health.status === 'degraded' ? '⚠️' : '❌'}
              </span>
              <div>
                <p className={`text-lg font-bold capitalize ${overallColor}`}>
                  System {health.status === 'healthy' ? 'Fully Operational' : health.status}
                </p>
                <p className="text-xs text-slate-400">
                  {lastChecked ? `Last checked: ${lastChecked.toLocaleTimeString()}` : 'Checking...'}
                </p>
              </div>
            </div>
            <div className="text-right">
              {latency !== undefined && (
                <div>
                  <p className="text-xs text-slate-500">API Latency</p>
                  <p className={`text-xl font-bold ${latency < 200 ? 'text-emerald-400' : latency < 500 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {latency}ms
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Services grid */}
      {loading && !health ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-24 rounded-xl" />
          ))}
        </div>
      ) : health ? (
        <SystemStatusPanel health={health} latency={latency} ready={ready ?? undefined} />
      ) : null}

      {/* Readiness */}
      {ready !== null && (
        <div className="mt-6 glass-card p-5 border border-white/5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-white mb-0.5">Readiness Probe</p>
              <p className="text-xs text-slate-500">Kubernetes / Docker health readiness status</p>
            </div>
            <span className={ready ? 'badge-true' : 'badge-false'}>
              {ready ? '✓ Ready' : '✗ Not Ready'}
            </span>
          </div>
        </div>
      )}

      {/* Version info */}
      {health && (
        <div className="mt-6 glass-card p-5 border border-white/5">
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">Platform Info</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <InfoItem label="Version" value={health.version || 'N/A'} />
            <InfoItem label="Environment" value={process.env.NODE_ENV || 'development'} />
            <InfoItem label="API Base" value={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'} />
          </div>
        </div>
      )}
    </div>
  );
}

const InfoItem: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div>
    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">{label}</p>
    <p className="text-sm text-slate-300 font-mono truncate">{value}</p>
  </div>
);
