'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';
import { useEffect, useState, useRef } from 'react';
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
  PanelLeftClose,
  PanelLeftOpen,
  HelpCircle,
  RotateCcw,
  Mail,
} from 'lucide-react';
import { WALKTHROUGH_STORAGE_KEY } from '@/components/walkthrough';

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
      <div className="flex justify-center mb-2">
        <a
          href="mailto:abel@aivaro-ai.com?subject=Upgrade%20Inquiry"
          title={expired ? 'Trial expired — Upgrade' : `${daysLeft}d left`}
          className={cn(
            "flex items-center justify-center w-9 h-9 rounded-lg transition-colors",
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
                <div className="h-full bg-primary-500 rounded-full transition-all" style={{ width: `${Math.min(100, (wfUsed / Math.max(wfLimit, 1)) * 100)}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-0.5">
                <span>Runs</span>
                <span className="font-medium">{runsUsed}/{runsLimit}</span>
              </div>
              <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary-500 rounded-full transition-all" style={{ width: `${Math.min(100, (runsUsed / Math.max(runsLimit, 1)) * 100)}%` }} />
              </div>
            </div>
          </div>
        </>
      )}
      <a
        href="mailto:abel@aivaro-ai.com?subject=Upgrade%20Inquiry"
        className={cn(
          "block w-full text-center py-1.5 rounded-lg font-medium text-xs transition-colors",
          expired ? "bg-red-600 text-white hover:bg-red-700" : "bg-primary-600 text-white hover:bg-primary-700"
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
  const [mounted, setMounted] = useState(false);
  const [showHelpMenu, setShowHelpMenu] = useState(false);
  const helpRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('aivaro_sidebar_collapsed');
      if (saved === 'true') setCollapsed(true);
    } catch {}
    setMounted(true);
  }, []);

  // Close help menu on outside click
  useEffect(() => {
    if (!showHelpMenu) return;
    const handler = (e: MouseEvent) => {
      if (helpRef.current && !helpRef.current.contains(e.target as Node)) setShowHelpMenu(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [showHelpMenu]);

  const toggleCollapse = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem('aivaro_sidebar_collapsed', String(next));
    window.dispatchEvent(new CustomEvent('sidebar-toggle', { detail: { collapsed: next } }));
  };

  // Prevent flash of wrong width on mount
  if (!mounted) return <aside className="fixed left-0 top-0 bottom-0 w-60 bg-white border-r border-gray-100 z-30" />;

  return (
    <aside
      className="fixed left-0 top-0 bottom-0 bg-white border-r border-gray-100 flex flex-col z-30 transition-[width] duration-200 ease-out"
      style={{ width: collapsed ? 64 : 240 }}
    >
      {/* Logo area */}
      <div className="h-14 flex items-center flex-shrink-0 border-b border-gray-100 px-2 gap-1">
        <button
          onClick={toggleCollapse}
          className="w-10 h-10 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors flex-shrink-0"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <PanelLeftOpen className="w-[18px] h-[18px]" /> : <PanelLeftClose className="w-[18px] h-[18px]" />}
        </button>
        <Link
          href="/app"
          className="flex items-center overflow-hidden transition-opacity duration-200"
          style={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
        >
          <span className="font-semibold text-gray-900 text-[15px] whitespace-nowrap">Aivaro</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden py-2 px-2">
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
                    'flex items-center h-10 rounded-lg transition-colors duration-150 overflow-hidden',
                    collapsed ? 'justify-center w-10 mx-auto' : 'px-3 gap-3',
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
                  )}
                >
                  <Icon className="w-[18px] h-[18px] flex-shrink-0" />
                  <span
                    className="text-sm whitespace-nowrap transition-opacity duration-200"
                    style={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto', overflow: 'hidden' }}
                  >
                    {item.label}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Trial Banner */}
      <TrialBanner collapsed={collapsed} />

      {/* Bottom: User + Settings + Help */}
      <div className="border-t border-gray-100 p-2 flex-shrink-0">
        {/* Action row: Settings + Help */}
        <div className={cn(
          "flex items-center mb-1",
          collapsed ? "flex-col gap-0.5" : "gap-0.5 px-1"
        )}>
          <Link
            href="/app/settings"
            title="Settings"
            className={cn(
              "flex items-center h-8 rounded-lg transition-colors duration-150 overflow-hidden",
              collapsed ? "justify-center w-10" : "px-2.5 gap-2 flex-1",
              pathname === '/app/settings'
                ? "bg-gray-100 text-gray-900"
                : "text-gray-400 hover:text-gray-600 hover:bg-gray-50"
            )}
          >
            <Settings className="w-4 h-4 flex-shrink-0" />
            <span
              className="text-xs whitespace-nowrap transition-opacity duration-200"
              style={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto', overflow: 'hidden' }}
            >
              Settings
            </span>
          </Link>

          <div ref={helpRef} className="relative">
            <button
              onClick={() => setShowHelpMenu(!showHelpMenu)}
              title="Help"
              className={cn(
                "flex items-center h-8 rounded-lg transition-colors duration-150 overflow-hidden",
                collapsed ? "justify-center w-10" : "px-2.5 gap-2",
                showHelpMenu
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-400 hover:text-gray-600 hover:bg-gray-50"
              )}
            >
              <HelpCircle className="w-4 h-4 flex-shrink-0" />
              <span
                className="text-xs whitespace-nowrap transition-opacity duration-200"
                style={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto', overflow: 'hidden' }}
              >
                Help
              </span>
            </button>

            {showHelpMenu && (
              <div className={cn(
                "absolute bottom-full mb-1 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50 w-44",
                collapsed ? "left-full ml-1" : "left-0"
              )}>
                <button
                  onClick={() => {
                    localStorage.removeItem(WALKTHROUGH_STORAGE_KEY);
                    window.location.reload();
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Restart Tour
                </button>
                <a
                  href="mailto:support@aivaro-ai.com"
                  className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <Mail className="w-3.5 h-3.5" />
                  Contact Support
                </a>
              </div>
            )}
          </div>
        </div>

        {/* User row */}
        <div
          className={cn(
            "flex items-center h-10 rounded-lg transition-colors duration-150 overflow-hidden",
            collapsed ? "justify-center w-10 mx-auto" : "px-2.5 gap-2.5 hover:bg-gray-50 cursor-default"
          )}
        >
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 text-white flex items-center justify-center font-medium text-xs flex-shrink-0">
            {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div
            className="flex-1 min-w-0 transition-opacity duration-200"
            style={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto', overflow: 'hidden' }}
          >
            <div className="text-sm font-medium text-gray-900 truncate leading-tight">
              {user?.full_name || user?.email?.split('@')[0]}
            </div>
          </div>
          <button
            onClick={logout}
            title="Sign out"
            className="p-1 rounded text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
            style={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto', overflow: 'hidden' }}
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
        {/* Collapsed: separate logout */}
        {collapsed && (
          <button
            onClick={logout}
            title="Sign out"
            className="flex items-center justify-center w-10 h-8 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors mx-auto mt-0.5"
          >
            <LogOut className="w-4 h-4" />
          </button>
        )}
      </div>
    </aside>
  );
}
