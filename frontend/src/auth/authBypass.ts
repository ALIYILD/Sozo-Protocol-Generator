/** Single source for dev-only auth bypass flag. */
export function isAuthBypassEnabled(): boolean {
  return import.meta.env.VITE_AUTH_BYPASS === 'true';
}
