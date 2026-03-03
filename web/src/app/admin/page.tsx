'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import {
  Users, Workflow, Play, MessageSquare, TrendingUp,
  ArrowLeft, RefreshCw, Shield, AlertTriangle, CheckCircle,
  Clock, Zap, Database, Link2, Brain, Activity,
} from 'lucide-react';

const colors = {
  primary: '#8b5cf6',
  primaryLight: '#a78bfa',
  secondary: '#6366f1',
  accent: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  textPrimary: '#e2e8f0',
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
  cardBg: 'rgba(15, 15, 35, 0.8)',
  inputBg: 'rgba(10, 10, 26, 0.6)',
  border: 'rgba(139, 92, 246, 0.2)',
};

interface Stats {
  users: { total: number; today: number; this_week: number; this_month: number; verified: number; unverified: number; by_plan: Record<string, number> };
  activity: { dau: number; wau: number };
  workflows: { total: number; active: number; this_week: number };
  executions: { total: number; today: number; this_week: number; by_status: Record<string, number> };
  chat: { conversations: number; messages: number; messages_today: number };
  connections: { total: number };
  knowledge: { total: number };
  trends: { signups_30d: { date: string; count: number }[]; executions_30d: { date: string; count: number }[] };
}

interface UserRow {
  id: string; email: string; full_name: string | null; plan: string;
  email_verified: boolean; onboarding_completed: boolean; created_at: string | null;
  trial_days_left: number | null; workflows: number; active_workflows: number;
  executions: number; total_runs_used: number; messages: number; connections: number;
  last_active: string | null; is_admin: boolean;
}

interface ActivityRow {
  id: string; workflow_name: string; user_email: string; user_name: string | null;
  status: string; started_at: string | null; completed_at: string | null;
  is_test: boolean; error: string | null;
}

function StatCard({ icon: Icon, label, value, sub, color }: { icon: any; label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div style={{
      background: colors.cardBg,
      backdropFilter: 'blur(20px)',
      border: `1px solid ${colors.border}`,
      borderRadius: '16px',
      padding: '20px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
    }}>
      <div style={{
        width: 44, height: 44, borderRadius: '12px',
        background: `${color || colors.primary}20`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Icon size={22} color={color || colors.primary} />
      </div>
      <div>
        <div style={{ fontSize: '24px', fontWeight: 700, color: colors.textPrimary, lineHeight: 1.2 }}>
          {value}
        </div>
        <div style={{ fontSize: '13px', color: colors.textMuted, marginTop: 2 }}>{label}</div>
        {sub && <div style={{ fontSize: '12px', color: colors.textSecondary, marginTop: 2 }}>{sub}</div>}
      </div>
    </div>
  );
}

function MiniChart({ data, color, height = 60 }: { data: number[]; color: string; height?: number }) {
  if (!data.length) return null;
  const max = Math.max(...data, 1);
  const w = 100 / data.length;
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height }}>
      {data.map((v, i) => (
        <div key={i} style={{
          flex: 1,
          height: `${Math.max((v / max) * 100, 4)}%`,
          background: v > 0 ? color : 'rgba(139,92,246,0.15)',
          borderRadius: '3px 3px 0 0',
          transition: 'height 0.3s ease',
          minHeight: 3,
        }} title={`${v}`} />
      ))}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    completed: { bg: 'rgba(16,185,129,0.15)', color: '#10b981' },
    running: { bg: 'rgba(59,130,246,0.15)', color: '#3b82f6' },
    failed: { bg: 'rgba(239,68,68,0.15)', color: '#ef4444' },
    paused: { bg: 'rgba(245,158,11,0.15)', color: '#f59e0b' },
    waiting_approval: { bg: 'rgba(245,158,11,0.15)', color: '#f59e0b' },
  };
  const s = map[status] || { bg: 'rgba(139,92,246,0.15)', color: colors.textMuted };
  return (
    <span style={{
      padding: '3px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: 600,
      background: s.bg, color: s.color, whiteSpace: 'nowrap',
    }}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}

function PlanBadge({ plan }: { plan: string }) {
  const map: Record<string, string> = { trial: '#f59e0b', starter: '#3b82f6', growth: '#8b5cf6', pro: '#10b981' };
  const c = map[plan] || colors.textMuted;
  return (
    <span style={{
      padding: '2px 8px', borderRadius: '5px', fontSize: '11px', fontWeight: 600,
      background: `${c}20`, color: c, textTransform: 'uppercase',
    }}>{plan}</span>
  );
}

export default function AdminDashboard() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const token = api.getToken();
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [activity, setActivity] = useState<ActivityRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<'overview' | 'users' | 'activity'>('overview');
  const [bootstrapping, setBootstrapping] = useState(false);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || '';
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [statsRes, usersRes, actRes] = await Promise.all([
        fetch(`${apiBase}/api/admin/stats`, { headers }),
        fetch(`${apiBase}/api/admin/users`, { headers }),
        fetch(`${apiBase}/api/admin/recent-activity?limit=30`, { headers }),
      ]);
      if (statsRes.status === 403) {
        setError('NOT_ADMIN');
        setLoading(false);
        return;
      }
      if (!statsRes.ok) throw new Error('Failed to fetch stats');
      setStats(await statsRes.json());
      setUsers(await usersRes.json());
      setActivity(await actRes.json());
    } catch (e: any) {
      setError(e.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!token) { router.push('/login'); return; }
    fetchAll();
  }, [token]);

  const handleBootstrap = async () => {
    setBootstrapping(true);
    try {
      const res = await fetch(`${apiBase}/api/admin/bootstrap`, { method: 'POST', headers });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail || 'Failed'); }
      await fetchAll();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBootstrapping(false);
    }
  };

  const timeAgo = (iso: string | null) => {
    if (!iso) return 'Never';
    const diff = Date.now() - new Date(iso + 'Z').getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  };

  // NOT ADMIN — show bootstrap
  if (error === 'NOT_ADMIN') {
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: '#050510', padding: 24,
      }}>
        <div style={{
          background: colors.cardBg, backdropFilter: 'blur(20px)', borderRadius: '24px',
          border: `1px solid ${colors.border}`, padding: '48px', textAlign: 'center', maxWidth: 440,
        }}>
          <Shield size={48} color={colors.primary} style={{ marginBottom: 20 }} />
          <h1 style={{ fontSize: 22, fontWeight: 700, color: colors.textPrimary, marginBottom: 8 }}>Admin Access Required</h1>
          <p style={{ fontSize: 14, color: colors.textMuted, marginBottom: 28, lineHeight: 1.6 }}>
            Your account doesn&apos;t have admin privileges yet. If you&apos;re the first user or your email is in ADMIN_EMAILS, click below.
          </p>
          <button onClick={handleBootstrap} disabled={bootstrapping} style={{
            padding: '14px 32px', background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
            border: 'none', borderRadius: '12px', color: 'white', fontSize: 16, fontWeight: 600,
            cursor: bootstrapping ? 'not-allowed' : 'pointer',
            opacity: bootstrapping ? 0.6 : 1,
          }}>
            {bootstrapping ? 'Activating...' : 'Activate Admin Access'}
          </button>
          <div style={{ marginTop: 20 }}>
            <button onClick={() => router.push('/app')} style={{
              background: 'none', border: 'none', color: colors.textMuted, fontSize: 14, cursor: 'pointer',
            }}>
              <ArrowLeft size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Back to App
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#050510', color: colors.textPrimary }}>
      {/* Header */}
      <div style={{
        borderBottom: `1px solid ${colors.border}`, padding: '16px 32px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        backdropFilter: 'blur(20px)', background: 'rgba(5,5,16,0.9)', position: 'sticky', top: 0, zIndex: 50,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <button onClick={() => router.push('/app')} style={{
            background: 'none', border: 'none', color: colors.textMuted, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: 6, fontSize: 14, padding: 0,
          }}>
            <ArrowLeft size={18} /> Back
          </button>
          <div style={{ width: 1, height: 24, background: colors.border }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Shield size={20} color={colors.primary} />
            <span style={{ fontSize: 18, fontWeight: 700 }}>Admin Dashboard</span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button onClick={fetchAll} disabled={loading} style={{
            background: 'rgba(139,92,246,0.1)', border: `1px solid ${colors.border}`, borderRadius: '8px',
            padding: '8px 16px', color: colors.textSecondary, fontSize: 13, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: 6,
          }}>
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 0, padding: '0 32px', borderBottom: `1px solid ${colors.border}` }}>
        {(['overview', 'users', 'activity'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: '14px 24px', background: 'none', border: 'none',
            borderBottom: tab === t ? `2px solid ${colors.primary}` : '2px solid transparent',
            color: tab === t ? colors.textPrimary : colors.textMuted,
            fontSize: 14, fontWeight: tab === t ? 600 : 400, cursor: 'pointer',
            textTransform: 'capitalize', transition: 'all 0.2s',
          }}>
            {t}
          </button>
        ))}
      </div>

      <div style={{ padding: '28px 32px', maxWidth: 1400, margin: '0 auto' }}>
        {loading && !stats ? (
          <div style={{ textAlign: 'center', padding: 80, color: colors.textMuted }}>
            <RefreshCw size={32} className="animate-spin" style={{ margin: '0 auto 16px' }} />
            Loading dashboard...
          </div>
        ) : error && error !== 'NOT_ADMIN' ? (
          <div style={{
            textAlign: 'center', padding: 80, color: colors.danger,
          }}>
            <AlertTriangle size={32} style={{ margin: '0 auto 16px' }} />
            {error}
          </div>
        ) : (
          <>
            {/* OVERVIEW TAB */}
            {tab === 'overview' && stats && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
                {/* Top stats grid */}
                <div style={{
                  display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 16,
                }}>
                  <StatCard icon={Users} label="Total Users" value={stats.users.total} sub={`+${stats.users.this_week} this week`} />
                  <StatCard icon={Activity} label="DAU" value={stats.activity.dau} sub={`WAU: ${stats.activity.wau}`} color={colors.accent} />
                  <StatCard icon={Workflow} label="Workflows" value={stats.workflows.total} sub={`${stats.workflows.active} active`} color={colors.secondary} />
                  <StatCard icon={Play} label="Executions" value={stats.executions.total} sub={`${stats.executions.today} today`} color="#3b82f6" />
                  <StatCard icon={MessageSquare} label="Chat Messages" value={stats.chat.messages} sub={`${stats.chat.messages_today} today`} color="#ec4899" />
                  <StatCard icon={Link2} label="Connections" value={stats.connections.total} color={colors.warning} />
                  <StatCard icon={Brain} label="Knowledge Entries" value={stats.knowledge.total} color={colors.accent} />
                  <StatCard icon={Zap} label="Conversations" value={stats.chat.conversations} color="#f97316" />
                </div>

                {/* Charts row */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div style={{
                    background: colors.cardBg, backdropFilter: 'blur(20px)',
                    border: `1px solid ${colors.border}`, borderRadius: '16px', padding: '24px',
                  }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: colors.textSecondary, marginBottom: 16 }}>
                      <TrendingUp size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
                      Signups (Last 30 Days)
                    </div>
                    <MiniChart data={stats.trends.signups_30d.map(d => d.count)} color={colors.primary} height={80} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 11, color: colors.textMuted }}>
                      <span>30d ago</span><span>Today</span>
                    </div>
                  </div>
                  <div style={{
                    background: colors.cardBg, backdropFilter: 'blur(20px)',
                    border: `1px solid ${colors.border}`, borderRadius: '16px', padding: '24px',
                  }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: colors.textSecondary, marginBottom: 16 }}>
                      <Play size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
                      Executions (Last 30 Days)
                    </div>
                    <MiniChart data={stats.trends.executions_30d.map(d => d.count)} color="#3b82f6" height={80} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 11, color: colors.textMuted }}>
                      <span>30d ago</span><span>Today</span>
                    </div>
                  </div>
                </div>

                {/* Plan breakdown + Execution status */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div style={{
                    background: colors.cardBg, backdropFilter: 'blur(20px)',
                    border: `1px solid ${colors.border}`, borderRadius: '16px', padding: '24px',
                  }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: colors.textSecondary, marginBottom: 16 }}>Users by Plan</div>
                    {Object.entries(stats.users.by_plan).map(([plan, count]) => (
                      <div key={plan} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0' }}>
                        <PlanBadge plan={plan} />
                        <span style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary }}>{count}</span>
                      </div>
                    ))}
                    <div style={{ borderTop: `1px solid ${colors.border}`, marginTop: 12, paddingTop: 12, display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                      <span style={{ color: colors.accent }}>
                        <CheckCircle size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />{stats.users.verified} verified
                      </span>
                      <span style={{ color: colors.warning }}>
                        <AlertTriangle size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />{stats.users.unverified} unverified
                      </span>
                    </div>
                  </div>
                  <div style={{
                    background: colors.cardBg, backdropFilter: 'blur(20px)',
                    border: `1px solid ${colors.border}`, borderRadius: '16px', padding: '24px',
                  }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: colors.textSecondary, marginBottom: 16 }}>Execution Status</div>
                    {Object.entries(stats.executions.by_status).map(([status, count]) => (
                      <div key={status} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0' }}>
                        <StatusBadge status={status} />
                        <span style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary }}>{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* USERS TAB */}
            {tab === 'users' && (
              <div style={{
                background: colors.cardBg, backdropFilter: 'blur(20px)',
                border: `1px solid ${colors.border}`, borderRadius: '16px', overflow: 'hidden',
              }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                      <tr style={{ borderBottom: `1px solid ${colors.border}` }}>
                        {['User', 'Plan', 'Workflows', 'Executions', 'Messages', 'Connections', 'Last Active', 'Joined'].map(h => (
                          <th key={h} style={{
                            padding: '14px 16px', textAlign: 'left', fontWeight: 600,
                            color: colors.textMuted, fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em',
                            whiteSpace: 'nowrap',
                          }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {users.map(u => (
                        <tr key={u.id} style={{ borderBottom: `1px solid rgba(139,92,246,0.1)` }}>
                          <td style={{ padding: '12px 16px' }}>
                            <div style={{ fontWeight: 600, color: colors.textPrimary }}>
                              {u.full_name || 'No name'}
                              {u.is_admin && <span style={{ fontSize: 10, color: colors.primary, marginLeft: 6 }}>ADMIN</span>}
                            </div>
                            <div style={{ fontSize: 12, color: colors.textMuted }}>{u.email}</div>
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            <PlanBadge plan={u.plan} />
                            {u.trial_days_left !== null && (
                              <div style={{ fontSize: 11, color: colors.warning, marginTop: 2 }}>
                                {u.trial_days_left}d left
                              </div>
                            )}
                          </td>
                          <td style={{ padding: '12px 16px', color: colors.textSecondary }}>
                            {u.workflows} <span style={{ color: colors.textMuted }}>({u.active_workflows} active)</span>
                          </td>
                          <td style={{ padding: '12px 16px', color: colors.textSecondary }}>{u.executions}</td>
                          <td style={{ padding: '12px 16px', color: colors.textSecondary }}>{u.messages}</td>
                          <td style={{ padding: '12px 16px', color: colors.textSecondary }}>{u.connections}</td>
                          <td style={{ padding: '12px 16px', color: colors.textMuted, fontSize: 12 }}>{timeAgo(u.last_active)}</td>
                          <td style={{ padding: '12px 16px', color: colors.textMuted, fontSize: 12 }}>
                            {u.created_at ? new Date(u.created_at + 'Z').toLocaleDateString() : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* ACTIVITY TAB */}
            {tab === 'activity' && (
              <div style={{
                background: colors.cardBg, backdropFilter: 'blur(20px)',
                border: `1px solid ${colors.border}`, borderRadius: '16px', overflow: 'hidden',
              }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                      <tr style={{ borderBottom: `1px solid ${colors.border}` }}>
                        {['Workflow', 'User', 'Status', 'Started', 'Duration', 'Error'].map(h => (
                          <th key={h} style={{
                            padding: '14px 16px', textAlign: 'left', fontWeight: 600,
                            color: colors.textMuted, fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em',
                            whiteSpace: 'nowrap',
                          }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {activity.map(a => {
                        const duration = a.started_at && a.completed_at
                          ? `${((new Date(a.completed_at + 'Z').getTime() - new Date(a.started_at + 'Z').getTime()) / 1000).toFixed(1)}s`
                          : a.status === 'running' ? 'Running...' : '—';
                        return (
                          <tr key={a.id} style={{ borderBottom: `1px solid rgba(139,92,246,0.1)` }}>
                            <td style={{ padding: '12px 16px', fontWeight: 500, color: colors.textPrimary }}>
                              {a.workflow_name}
                              {a.is_test && <span style={{ fontSize: 10, color: colors.warning, marginLeft: 6 }}>TEST</span>}
                            </td>
                            <td style={{ padding: '12px 16px' }}>
                              <div style={{ color: colors.textSecondary }}>{a.user_name || a.user_email}</div>
                            </td>
                            <td style={{ padding: '12px 16px' }}><StatusBadge status={a.status} /></td>
                            <td style={{ padding: '12px 16px', color: colors.textMuted, fontSize: 12 }}>{timeAgo(a.started_at)}</td>
                            <td style={{ padding: '12px 16px', color: colors.textSecondary, fontSize: 12 }}>{duration}</td>
                            <td style={{ padding: '12px 16px', color: colors.danger, fontSize: 12, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {a.error || '—'}
                            </td>
                          </tr>
                        );
                      })}
                      {activity.length === 0 && (
                        <tr><td colSpan={6} style={{ padding: 40, textAlign: 'center', color: colors.textMuted }}>No recent activity</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
