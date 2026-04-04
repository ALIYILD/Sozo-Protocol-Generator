import type { FutureConfig } from 'react-router';

/** Opt into React Router v7 behaviors early (quiets upgrade warnings, matches v7). */
export const ROUTER_V7_FUTURE_FLAGS: Partial<FutureConfig> = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
};
