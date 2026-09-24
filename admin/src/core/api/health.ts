import { client } from './generated/client/client.gen'
import { healthApiV1HealthGet, healthDetailApiV1HealthDetailGet } from './generated/client'

export type HealthStatus = 'ok' | 'degraded' | 'unavailable';

export interface HealthSummary {
  status: HealthStatus;
  database: HealthStatus;
  redis: HealthStatus;
  tasks: { total: number; pending: number; running: number; failed: number; dead: number };
}

type HealthPayload = {
  status?: string;
  database?: { status?: string };
  redis?: { status?: string };
  tasks?: Partial<HealthSummary['tasks']>;
};

function normalizeStatus(value?: string): HealthStatus {
  if (value === 'ok' || value === 'up') return 'ok';
  if (value === 'degraded') return 'degraded';
  return 'unavailable';
}

export function normalizeHealthPayload(payload: HealthPayload): HealthSummary {
  return {
    status: normalizeStatus(payload.status),
    database: normalizeStatus(payload.database?.status),
    redis: normalizeStatus(payload.redis?.status),
    tasks: {
      total: payload.tasks?.total ?? 0,
      pending: payload.tasks?.pending ?? 0,
      running: payload.tasks?.running ?? 0,
      failed: payload.tasks?.failed ?? 0,
      dead: payload.tasks?.dead ?? 0,
    },
  };
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthSummary> {
  client.setConfig({ baseUrl: '' });
  const payload = await healthApiV1HealthGet({ signal, throwOnError: true, responseStyle: 'data' });
  return normalizeHealthPayload(payload as HealthPayload);
}

export async function fetchHealthDetail(signal?: AbortSignal): Promise<HealthSummary> {
  client.setConfig({ baseUrl: '' });
  const payload = await healthDetailApiV1HealthDetailGet({ signal, throwOnError: true, responseStyle: 'data' });
  return normalizeHealthPayload(payload as HealthPayload);
}
