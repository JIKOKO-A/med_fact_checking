'use client';

import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area,
} from 'recharts';
import { AnalyticsData, ConfidenceDistribution } from '@/services/api';

interface AnalyticsDashboardProps {
  analytics: AnalyticsData;
  confidenceDistribution?: ConfidenceDistribution | null;
}

const LABEL_COLORS = {
  true: '#10b981',
  false: '#ef4444',
  partial: '#f59e0b',
  unverifiable: '#64748b',
};

const PIE_COLORS = [LABEL_COLORS.true, LABEL_COLORS.false, LABEL_COLORS.partial, LABEL_COLORS.unverifiable];

const CustomTooltipStyle = {
  contentStyle: { background: '#0f1629', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f1f5f9', fontSize: '12px' },
  labelStyle: { color: '#94a3b8' },
};

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ analytics, confidenceDistribution }) => {
  const labelData = [
    { name: 'True', value: analytics.true_count, color: LABEL_COLORS.true },
    { name: 'False', value: analytics.false_count, color: LABEL_COLORS.false },
    { name: 'Partial', value: analytics.partial_count, color: LABEL_COLORS.partial },
    { name: 'Unverifiable', value: analytics.unverifiable_count, color: LABEL_COLORS.unverifiable },
  ];

  const domainData = Object.entries(analytics.domain_distribution)
    .sort(([, a], [, b]) => b - a)
    .map(([domain, count]) => ({ name: domain.replace(/_/g, ' '), value: count }));

  const confData = confidenceDistribution
    ? Object.entries(confidenceDistribution.confidence_distribution).map(([range, count]) => ({
        range: range.split('-')[0],
        count,
      }))
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Verified"
          value={analytics.total_verified.toLocaleString()}
          subtitle="All time"
          icon="🔍"
          color="blue"
        />
        <KPICard
          title="Avg Confidence"
          value={`${(analytics.avg_confidence_score * 100).toFixed(1)}%`}
          subtitle="Across all claims"
          icon="🎯"
          color="cyan"
        />
        <KPICard
          title="Misinformation Rate"
          value={`${(analytics.misinformation_rate * 100).toFixed(1)}%`}
          subtitle="False claims detected"
          icon="⚠️"
          color="red"
        />
        <KPICard
          title="Avg Processing"
          value={`${analytics.avg_processing_time_ms.toFixed(0)}ms`}
          subtitle="Per verification"
          icon="⚡"
          color="purple"
        />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pie chart */}
        <ChartCard title="Verdict Distribution">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={labelData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={100}
                paddingAngle={3}
                dataKey="value"
              >
                {labelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                {...CustomTooltipStyle}
                formatter={(value) => [`${value} claims`, '']}
              />
              <Legend
                formatter={(value) => <span style={{ color: '#94a3b8', fontSize: '12px' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Domain bar chart */}
        <ChartCard title="Claims by Medical Domain">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={domainData} layout="vertical" margin={{ left: 20, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" width={110} tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip {...CustomTooltipStyle} formatter={(v) => [`${v} claims`, '']} />
              <Bar dataKey="value" fill="url(#barGradient)" radius={[0, 4, 4, 0]}>
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Daily trend */}
      {analytics.daily_trend.length > 0 && (
        <ChartCard title="Daily Verification Trend">
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={analytics.daily_trend} margin={{ left: 0 }}>
              <defs>
                <linearGradient id="trueGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="falseGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip {...CustomTooltipStyle} />
              <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: '12px' }}>{v}</span>} />
              <Area type="monotone" dataKey="true" stroke={LABEL_COLORS.true} fill="url(#trueGrad)" strokeWidth={2} name="True" />
              <Area type="monotone" dataKey="false" stroke={LABEL_COLORS.false} fill="url(#falseGrad)" strokeWidth={2} name="False" />
              <Line type="monotone" dataKey="partial" stroke={LABEL_COLORS.partial} strokeWidth={2} dot={false} name="Partial" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      )}

      {/* Confidence distribution */}
      {confData.length > 0 && (
        <ChartCard title="Confidence Score Distribution">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={confData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="range" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${(parseFloat(v) * 100).toFixed(0)}%`} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip {...CustomTooltipStyle} labelFormatter={(v) => `Score: ${(parseFloat(v) * 100).toFixed(0)}–${(parseFloat(v) * 100 + 10).toFixed(0)}%`} formatter={(v) => [`${v} claims`, '']} />
              <Bar dataKey="count" fill="url(#confGradient)" radius={[4, 4, 0, 0]}>
                <defs>
                  <linearGradient id="confGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="100%" stopColor="#3b82f6" />
                  </linearGradient>
                </defs>
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      )}
    </div>
  );
};

// ─── Sub-components ──────────────────────────────────

const KPICard: React.FC<{ title: string; value: string; subtitle: string; icon: string; color: string }> = ({
  title, value, subtitle, icon, color,
}) => {
  const border: Record<string, string> = {
    blue: 'border-blue-500/20',
    cyan: 'border-cyan-500/20',
    red: 'border-red-500/20',
    purple: 'border-purple-500/20',
  };
  const text: Record<string, string> = {
    blue: 'text-blue-400',
    cyan: 'text-cyan-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
  };

  return (
    <div className={`kpi-card border ${border[color]}`}>
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs text-slate-500 uppercase tracking-wider">{title}</p>
        <span className="text-lg">{icon}</span>
      </div>
      <p className={`text-2xl font-bold ${text[color]} mb-0.5`}>{value}</p>
      <p className="text-xs text-slate-500">{subtitle}</p>
    </div>
  );
};

const ChartCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="glass-card p-5 border border-white/5">
    <h3 className="text-sm font-semibold text-slate-300 mb-4">{title}</h3>
    {children}
  </div>
);
