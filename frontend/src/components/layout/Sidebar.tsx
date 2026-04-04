import { NavLink } from 'react-router-dom';
import clsx from 'clsx';
import {
  LayoutDashboard,
  FileText,
  Search,
  Shield,
  Sliders,
  Users,
  ShieldAlert,
  Brain,
} from 'lucide-react';
import { canAccessAdmin } from '../../auth/permissions';
import { useAuth } from '../../hooks/useAuth';
import type { User } from '../../types';

type NavItem = {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  badge?: string;
  visibleIf?: (user: User | null | undefined) => boolean;
};

const navItems: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/protocols', label: 'Protocols', icon: FileText },
  { to: '/evidence', label: 'Evidence', icon: Search },
  { to: '/safety', label: 'Safety', icon: ShieldAlert },
  { to: '/personalization', label: 'Personalization', icon: Sliders },
  { to: '/patients', label: 'Patients', icon: Users, badge: 'V2' },
  {
    to: '/admin/audit',
    label: 'Admin',
    icon: Shield,
    visibleIf: canAccessAdmin,
  },
];

export default function Sidebar() {
  const { user } = useAuth();
  const visible = navItems.filter(
    (item) => !item.visibleIf || item.visibleIf(user),
  );

  return (
    <aside className="flex h-full w-64 flex-col border-r border-gray-200 bg-white">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-gray-200 px-6">
        <Brain className="h-8 w-8 text-sozo-primary" />
        <span className="text-xl font-bold text-sozo-primary">SOZO</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {visible.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sozo-primary text-white'
                  : 'text-gray-700 hover:bg-gray-100',
              )
            }
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
            {item.badge && (
              <span className="ml-auto rounded bg-sozo-secondary/10 px-1.5 py-0.5 text-xs font-medium text-sozo-secondary">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-200 px-6 py-4">
        <p className="text-xs text-gray-400">SOZO Protocol Generator</p>
        <p className="text-xs text-gray-400">v0.2.0</p>
      </div>
    </aside>
  );
}
