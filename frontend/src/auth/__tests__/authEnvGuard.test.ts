import { describe, expect, it } from 'vitest';
import { assertProductionAuthBypassNotEnabled } from '../authEnvGuard';

describe('assertProductionAuthBypassNotEnabled', () => {
  it('throws when env looks like a production bundle with bypass on', () => {
    expect(() =>
      assertProductionAuthBypassNotEnabled({
        PROD: true,
        VITE_AUTH_BYPASS: 'true',
      }),
    ).toThrow(/VITE_AUTH_BYPASS cannot be enabled/);
  });

  it('does not throw when bypass is on in development', () => {
    expect(() =>
      assertProductionAuthBypassNotEnabled({
        PROD: false,
        VITE_AUTH_BYPASS: 'true',
      }),
    ).not.toThrow();
  });

  it('does not throw in production when bypass is off', () => {
    expect(() =>
      assertProductionAuthBypassNotEnabled({
        PROD: true,
        VITE_AUTH_BYPASS: undefined,
      }),
    ).not.toThrow();
  });
});
