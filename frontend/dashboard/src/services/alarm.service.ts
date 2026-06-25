/**
 * Alarm service — the only file allowed to call fetch() for alarm-related API access.
 *
 * Uses NEXT_PUBLIC_API_URL from the monorepo root .env.
 * Endpoints:
 *   GET /api/v1/alarm/state  — current alarm state
 *   GET /api/v1/events       — paginated event history
 *   GET /api/v1/analytics    — analytics metrics
 */

import type { AlarmState, EventPage, AnalyticsMetrics } from '@/types/alarm.types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8080';

export async function getAlarmState(): Promise<AlarmState> {
  const res = await fetch(`${BASE_URL}/api/v1/alarm/state`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`Failed to fetch alarm state: ${res.status}`);
  return res.json();
}

export async function getEvents(
  limit = 50,
  offset = 0,
): Promise<EventPage> {
  const res = await fetch(
    `${BASE_URL}/api/v1/events?limit=${limit}&offset=${offset}`,
    { cache: 'no-store' },
  );
  if (!res.ok) throw new Error(`Failed to fetch events: ${res.status}`);
  return res.json();
}

export async function getAnalytics(): Promise<AnalyticsMetrics> {
  const res = await fetch(`${BASE_URL}/api/v1/analytics`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch analytics: ${res.status}`);
  return res.json();
}
