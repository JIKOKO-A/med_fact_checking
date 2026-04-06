'use client';

import React from 'react';
import { HealthStatus } from '@/services/api';

interface StatusCardProps {
  name: string;
  status: string;
  icon: string;
  detail?: string;
}

export const StatusCard: React.FC<StatusCardProps> = ({ name, status, icon, detail }) => {
  const isHealthy = status === 'healthy' || status === 'true';
  const isDegraded = status === 'degraded';
  const isUnhealthy = !isHealthy && !isDegraded;

  const color = isHealthy ? 'emerald' : isDegraded ? 'yellow' : 'red';
  const dotClass = isHealthy
    ? 'status-dot-healthy animate-pulse-glow'
    : isDegraded
    ? 'status-dot-degraded'
    : 'status-dot-unhealthy';
  const borderColor = isHealthy
    ? 'border-emerald-500/20 hover:border-emerald-500/40'
    : isDegraded
    ? 'border-yellow-500/20 hover:border-yellow-500/40'
    : 'border-red-500/20 hover:border-red-500/40';
  const labelColor = isHealthy ? 'text-emerald-400' : isDegraded ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className={`glass-card p-5 border ${borderColor} transition-all duration-300`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center text-lg">
            {icon}
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{name}</p>
            {detail && <p className="text-xs text-slate-500">{detail}</p>}
          </div>
        </div>
        <div className={dotClass} />
      </div>
      <span className={`text-xs font-semibold uppercase tracking-wider ${labelColor}`}>
        {status === 'true' ? 'Online' : status === 'false' ? 'Offline' : status}
      </span>
    </div>
  );
};

interface SystemStatusProps {
  health: HealthStatus;
  latency?: number;
  ready?: boolean;
}

export const SystemStatusPanel: React.FC<SystemStatusProps> = ({ health, latency, ready }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatusCard
        name="Database"
        status={health.database}
        icon="🗄️"
        detail="PostgreSQL"
      />
      <StatusCard
        name="Cache"
        status={health.redis}
        icon="⚡"
        detail="Redis"
      />
      <StatusCard
        name="ML Service"
        status={health.ml_service}
        icon="🤖"
        detail="Verification Engine"
      />
      <StatusCard
        name="API"
        status={health.status}
        icon="🌐"
        detail={latency !== undefined ? `${latency}ms latency` : `v${health.version}`}
      />
    </div>
  );
};
