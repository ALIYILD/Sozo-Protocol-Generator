import { describe, expect, it } from 'vitest';
import { protocolIdFromGraphOutput } from '../protocolIdFromGraphOutput';

describe('protocolIdFromGraphOutput', () => {
  it('returns undefined when output is missing or empty', () => {
    expect(protocolIdFromGraphOutput(undefined)).toBeUndefined();
    expect(protocolIdFromGraphOutput({})).toBeUndefined();
  });

  it('returns trimmed string protocol_id when present', () => {
    expect(
      protocolIdFromGraphOutput({ protocol_id: '  abc-123  ' }),
    ).toBe('abc-123');
  });

  it('ignores non-string protocol_id', () => {
    expect(protocolIdFromGraphOutput({ protocol_id: 42 })).toBeUndefined();
  });
});
