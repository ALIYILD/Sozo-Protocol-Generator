import { useState, useEffect } from 'react';

const STORAGE_KEY = 'sozo-theme';

function getInitialDark(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored !== null) {
    return stored === 'dark';
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

export function useDarkMode(): [boolean, () => void] {
  const [isDark, setIsDark] = useState<boolean>(getInitialDark);

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggle = () => setIsDark((prev) => !prev);

  return [isDark, toggle];
}
