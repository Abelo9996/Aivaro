'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/app', label: 'Dashboard', icon: '🏠', walkthrough: 'nav-dashboard' },
  { href: '/app/workflows', label: 'Workflows', icon: '⚡', walkthrough: 'nav-workflows' },
  { href: '/app/templates', label: 'Templates', icon: '📋', walkthrough: 'nav-templates' },
  { href: '/app/executions', label: 'Run History', icon: '📊', walkthrough: 'nav-executions' },
  { href: '/app/approvals', label: 'Approvals', icon: '✅', walkthrough: 'nav-approvals' },
  { href: '/app/connections', label: 'Connections', icon: '🔗', walkthrough: 'nav-connections' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6">
        <Link href="/app" className="text-2xl font-bold text-primary-600">
          Aivaro
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || 
              (item.href !== '/app' && pathname.startsWith(item.href));
            
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  data-walkthrough={item.walkthrough}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition',
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-50'
                  )}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-medium">
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">
              {user?.full_name || user?.email}
            </div>
            <button
              onClick={logout}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}
