'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import {
  Zap,
  FileText,
  BarChart3,
  CheckCircle2,
  Link2,
  LogOut,
  MessageSquare,
  BookOpen,
  Sparkles,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const navItems = [
  { href: '/app', label: 'Chat', Icon: MessageSquare, walkthrough: 'nav-dashboard' },
  { href: '/app/workflows', label: 'Workflows', Icon: Zap, walkthrough: 'nav-workflows' },
  { href: '/app/templates', label: 'Templates', Icon: FileText, walkthrough: 'nav-templates' },
  { href: '/app/executions', label: 'Run History', Icon: BarChart3, walkthrough: 'nav-executions' },
  { href: '/app/approvals', label: 'Approvals', Icon: CheckCircle2, walkthrough: 'nav-approvals' },
  { href: '/app/knowledge', label: 'Knowledge Base', Icon: BookOpen, walkthrough: 'nav-knowledge' },
  { href: '/app/connections', label: 'Connections', Icon: Link2, walkthrough: 'nav-connections' },
];

function TrialBanner({ collapsed }: { collapsed: boolean }) {
  const [usage, setUsage] = useState<any>(null);

  useEffect(() => {
    const fetchUsage = () => api.getUsage().then(setUsage).catch(() => {});
    fetchUsage();
    const interval = setInterval(fetchUsage, 60000);
    const onFocus = () => fetchUsage();
    const onWorkflowRun = () => fetchUsage();
    window.addEventListener('focus', onFocus);
    window.addEventListener('workflow-run', onWorkflowRun);
    return () => { clearInterval(interval); window.removeEventListener('focus', onFocus); window.removeEventListener('workflow-run', onWorkflowRun); };
  }, []);

  if (!usage || !usage.is_trial) return null;

  const expired = usage.trial_expired;
  const daysLeft = usage.trial_days_left;
  const runsUsed = usage.usage?.total_runs?.used || 0;
  const runsLimit = usage.usage?.total_runs?.limit || 10;
  const wfUsed = usage.usage?.active_workflows?.used || 0;
  const wfLimit = usage.usage?.active_workflows?.limit || 1;

  if (collapsed) {
    return (
      <div className="mx-auto mb-3">
        <a
          href="mailto:abel@aivaro-ai.com?subject=Upgrade%20Inquiry"
          title={expired ? 'Trial expired — Upgrade' : `${daysLeft}d left`}
          className={cn(
            "flex items-center justify-center w-10 h-10 rounded-xl transition-colors",
            expired ? "bg-red-100 text-red-600 hover:bg-red-200" : "bg-primary-100 text-primary-600 hover:bg-primary-200"
          )}
        >
          <Sparkles className="w-4 h-4" />
        </a>
      </div>
    );
  }

  return (
    <div className={cn(
      "mx-3 mb-3 rounded-xl p-3 text-xs",
      expired
        ? "bg-red-50 border border-red-200"
        : daysLeft <= 2
          ? "bg-amber-50 border border-amber-200"
          : "bg-primary-50 border border-primary-100"
    )}>
      {expired ? (
        <>
          <p className="font-semibold text-red-700 mb-1">Trial Expired</p>
          <p className="text-red-600 mb-2">Upgrade to continue using Aivaro.</p>
        </>
      ) : (
        <>
          <p className="font-semibold text-gray-800 mb-1">
            Free Trial — {daysLeft} day{daysLeft !== 1 ? 's' : ''} left
          </p>
          <div className="space-y-1.5 text-gray-600 mb-2">
            <div>
              <div className="flex justify-between mb-0.5">
                <span>Workflows</span>
                <span className="font-medium">{wfUsed}/{wfLimit}</span>
              </div>
              <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary-500 rounded-full" style={{ width: `${Math.min(100, (wfUsed / Math.max(wfLimit, 1)) * 100)}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-0.5">
                <span>Runs</span>
                <span className="font-medium">{runsUsed}/{runsLimit}</span>
              </div>
              <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary-500 rounded-full" style={{ width: `${Math.min(100, (runsUsed / Math.max(runsLimit, 1)) * 100)}%` }} />
              </div>
            </div>
          </div>
        </>
      )}
      <a
        href="mailto:abel@aivaro-ai.com?subject=Upgrade%20Inquiry"
        className={cn(
          "block w-full text-center py-1.5 rounded-lg font-medium text-xs transition-colors",
          expired
            ? "bg-red-600 text-white hover:bg-red-700"
            : "bg-primary-600 text-white hover:bg-primary-700"
        )}
      >
        <Sparkles className="w-3 h-3 inline mr-1" />
        Upgrade
      </a>
    </div>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  // Persist collapse state
  useEffect(() => {
    try {
      const saved = localStorage.getItem('aivaro_sidebar_collapsed');
      if (saved === 'true') setCollapsed(true);
    } catch {}
  }, []);

  const toggleCollapse = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem('aivaro_sidebar_collapsed', String(next));
    // Notify layout of width change
    window.dispatchEvent(new CustomEvent('sidebar-toggle', { detail: { collapsed: next } }));
  };

  const sidebarWidth = collapsed ? 'w-[72px]' : 'w-60';

  return (
    <aside className={cn(
      "fixed left-0 top-0 bottom-0 bg-white border-r border-gray-100 flex flex-col transition-all duration-200 ease-in-out z-30",
      sidebarWidth,
    )}>
      {/* Logo + Collapse Toggle */}
      <div className={cn("flex items-center border-b border-gray-100", collapsed ? "justify-center p-4" : "justify-between px-5 py-4")}>
        <Link href="/app" className="flex items-center gap-2 min-w-0">
          {collapsed ? (
            <Image
              src="/logo-icon.png"
              alt="Aivaro"
              width={28}
              height={28}
              className="w-7 h-7"
              priority
              onError={(e) => {
                // Fallback if logo-icon doesn't exist
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          ) : (
            <Image
              src="/logo-dark.png"
              alt="Aivaro"
              width={120}
              height={42}
              className="h-8 w-auto"
              priority
            />
          )}
        </Link>
        {!collapsed && (
          <button
            onClick={toggleCollapse}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            title="Collapse sidebar"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 overflow-y-auto">
        <ul className="space-y-0.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href ||
              (item.href !== '/app' && pathname.startsWith(item.href));
            const Icon = item.Icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  data-walkthrough={item.walkthrough}
                  title={collapsed ? item.label : undefined}
                  className={cn(
                    'flex items-center gap-3 rounded-xl transition-all duration-150',
                    collapsed ? 'justify-center px-0 py-2.5 mx-auto w-12' : 'px-3 py-2.5',
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium shadow-sm shadow-primary-100/50'
                      : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <Icon className={cn("flex-shrink-0", isActive ? "w-[18px] h-[18px]" : "w-[18px] h-[18px]")} />
                  {!collapsed && <span className="text-sm truncate">{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Expand button when collapsed */}
      {collapsed && (
        <div className="px-2 mb-2">
          <button
            onClick={toggleCollapse}
            className="w-full flex items-center justify-center p-2.5 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            title="Expand sidebar"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Trial Banner */}
      <TrialBanner collapsed={collapsed} />

      {/* User + Settings */}
      <div className="border-t border-gray-100 p-2">
        {collapsed ? (
          <div className="flex flex-col items-center gap-1">
            <Link
              href="/app/settings"
              title="Settings"
              className={cn(
                "flex items-center justify-center w-10 h-10 rounded-xl transition-colors",
                pathname === '/app/settings'
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-400 hover:text-gray-600 hover:bg-gray-50"
              )}
            >
              <Settings className="w-[18px] h-[18px]" />
            </Link>
            <button
              onClick={logout}
              title="Sign out"
              className="flex items-center justify-center w-10 h-10 rounded-xl text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-[18px] h-[18px]" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-gray-50 transition-colors group">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 text-white flex items-center justify-center font-medium text-sm flex-shrink-0">
              {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">
                {user?.full_name || user?.email?.split('@')[0]}
              </div>
              <div className="text-xs text-gray-400 truncate">
                {user?.email}
              </div>
            </div>
            <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
              <Link
                href="/app/settings"
                className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                title="Settings"
              >
                <Settings className="w-3.5 h-3.5" />
              </Link>
              <button
                onClick={logout}
                className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                title="Sign out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
