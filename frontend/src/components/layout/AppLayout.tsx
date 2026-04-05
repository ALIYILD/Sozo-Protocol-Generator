import { useState } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { AlertTriangle, LogOut, Menu, Moon, Sun, User, X } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import { useDarkMode } from '../../hooks/useDarkMode';
import { getHealth } from '../../api/health';
import Sidebar from './Sidebar';

const API_KEY_BANNER_DISMISS_KEY = 'sozo_api_key_banner_dismissed';

/**
 * Safely probe `checks.anthropic_key_configured` on a loose health payload.
 * Returns `true` only when the backend has explicitly reported the key as
 * missing. Any other shape (field absent, request failed, unexpected types)
 * returns `false` so the banner stays hidden — it's a helpful hint, not a gate.
 */
function anthropicKeyMissing(health: Record<string, unknown> | undefined): boolean {
  if (!health) return false;
  const checks = health.checks;
  if (!checks || typeof checks !== 'object') return false;
  const value = (checks as Record<string, unknown>).anthropic_key_configured;
  return value === false;
}

export default function AppLayout() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isDark, toggleDark] = useDarkMode();
  const [bannerDismissed, setBannerDismissed] = useState<boolean>(() => {
    try {
      return sessionStorage.getItem(API_KEY_BANNER_DISMISS_KEY) === '1';
    } catch {
      return false;
    }
  });

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    staleTime: 60_000,
    refetchOnWindowFocus: false,
    retry: false,
  });

  const showApiKeyBanner = !bannerDismissed && anthropicKeyMissing(health);

  const dismissBanner = () => {
    try {
      sessionStorage.setItem(API_KEY_BANNER_DISMISS_KEY, '1');
    } catch {
      /* sessionStorage unavailable — dismiss in-memory only */
    }
    setBannerDismissed(true);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-sozo-surface dark:bg-gray-950">
      {/* Mobile backdrop — sits behind the sidebar overlay */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex flex-1 flex-col overflow-hidden md:ml-64">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 dark:bg-gray-900 dark:border-gray-700">
          {/* Hamburger — mobile only */}
          <button
            className="md:hidden flex items-center justify-center rounded-md p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
            onClick={() => setSidebarOpen((prev) => !prev)}
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
          >
            {sidebarOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>

          {/* Desktop header left spacer */}
          <div className="hidden md:block" />

          <div className="flex items-center gap-4">
            {user && (
              <Link
                to="/profile"
                className="flex items-center gap-2 rounded-md px-2 py-1 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                title="View profile & change password"
              >
                <User className="h-4 w-4" />
                <span>{user.email}</span>
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-medium text-gray-500 dark:bg-gray-700 dark:text-gray-400">
                  {user.role}
                </span>
              </Link>
            )}
            <button
              onClick={toggleDark}
              className="flex items-center justify-center rounded-md p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </button>
            <button
              onClick={logout}
              className="flex items-center gap-1 rounded-md px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6 dark:bg-gray-950">
          {showApiKeyBanner && (
            <div
              role="alert"
              className="mb-4 flex items-start gap-3 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200"
            >
              <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600 dark:text-amber-400" />
              <div className="flex-1">
                <span className="font-semibold">Generation disabled</span>
                {' — '}
                <code className="rounded bg-amber-100 px-1 py-0.5 font-mono text-xs dark:bg-amber-900/60">
                  ANTHROPIC_API_KEY
                </code>
                {" isn't configured on the server. Protocol generation will fail until an admin sets it. (Contact your ops team.)"}
              </div>
              <button
                type="button"
                onClick={dismissBanner}
                className="flex-shrink-0 rounded p-1 text-amber-700 hover:bg-amber-100 dark:text-amber-300 dark:hover:bg-amber-900/60"
                aria-label="Dismiss warning"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  );
}
