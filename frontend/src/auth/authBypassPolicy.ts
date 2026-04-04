/**
 * Pure policy for when auth bypass is unsafe (production bundles / `vite build`).
 * No `import.meta` — safe to import from `vite.config.ts`.
 */

export function isUnsafeProductionAuthBypass(
  isProd: boolean,
  viteAuthBypass: string | undefined,
): boolean {
  return isProd && viteAuthBypass === 'true';
}
