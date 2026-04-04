/**
 * Runtime guard: never ship production bundles with auth bypass enabled.
 */

import { isUnsafeProductionAuthBypass } from './authBypassPolicy';

export type AuthViteEnv = {
  readonly PROD: boolean;
  readonly VITE_AUTH_BYPASS?: string;
};

/** Call once at startup (e.g. main.tsx). Throws if misconfigured. */
export function assertProductionAuthBypassNotEnabled(
  env: AuthViteEnv = import.meta.env,
): void {
  if (isUnsafeProductionAuthBypass(env.PROD, env.VITE_AUTH_BYPASS)) {
    throw new Error(
      'VITE_AUTH_BYPASS cannot be enabled in production builds. ' +
        'Remove VITE_AUTH_BYPASS from the environment used for vite build.',
    );
  }
}
