import { describe, expect, it } from 'vitest';
import { normalizeHealthPayload } from './health';

describe('normalizeHealthPayload', () => {
  it('normalizes the P2 health contract for the admin shell', () => {
    expect(normalizeHealthPayload({ status: 'ok', database: { status: 'up' }, redis: { status: 'down' }, tasks: { pending: 2 } })).toEqual({
      status: 'ok',
      database: 'ok',
      redis: 'unavailable',
      tasks: { total: 0, pending: 2, running: 0, failed: 0, dead: 0 },
    });
  });

  it('marks missing dependencies as unavailable instead of claiming healthy', () => {
    expect(normalizeHealthPayload({ status: 'ok' })).toEqual({
      status: 'ok',
      database: 'unavailable',
      redis: 'unavailable',
      tasks: { total: 0, pending: 0, running: 0, failed: 0, dead: 0 },
    });
  });
});
