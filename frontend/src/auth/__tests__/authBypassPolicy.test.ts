import { describe, expect, it } from 'vitest';
import { isUnsafeProductionAuthBypass } from '../authBypassPolicy';

describe('isUnsafeProductionAuthBypass (production / build guard policy)', () => {
  it('is false in dev-like environments even if bypass is true', () => {
    expect(isUnsafeProductionAuthBypass(false, 'true')).toBe(false);
  });

  it('is false when bypass is unset in production', () => {
    expect(isUnsafeProductionAuthBypass(true, undefined)).toBe(false);
    expect(isUnsafeProductionAuthBypass(true, 'false')).toBe(false);
    expect(isUnsafeProductionAuthBypass(true, '')).toBe(false);
  });

  it('is true only when production/build flag and bypass are both enabled', () => {
    expect(isUnsafeProductionAuthBypass(true, 'true')).toBe(true);
  });
});
