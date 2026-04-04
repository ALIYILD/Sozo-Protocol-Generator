import { describe, expect, it } from 'vitest';
import { auditFiltersToQueryParams } from '../audit';

describe('auditFiltersToQueryParams', () => {
  it('drops empty and whitespace-only values', () => {
    expect(
      auditFiltersToQueryParams({
        entity_type: '',
        action: '   ',
        actor: 'a@b.com',
      }),
    ).toEqual({ actor: 'a@b.com' });
  });

  it('trims and passes through set filter keys', () => {
    expect(
      auditFiltersToQueryParams({
        entity_type: ' protocol ',
        date_from: '2025-01-01',
        node_name: 'compose',
      }),
    ).toEqual({
      entity_type: 'protocol',
      date_from: '2025-01-01',
      node_name: 'compose',
    });
  });
});
