'use client';

/**
 * useEvents — polls GET /api/v1/events every 5 seconds.
 * Returns the event list and total count.
 */

import { useEffect, useState } from 'react';
import { getEvents } from '@/services/alarm.service';
import type { AlarmEvent } from '@/types/alarm.types';

const POLL_INTERVAL_MS = 5000;

export function useEvents(limit = 50) {
  const [events, setEvents] = useState<AlarmEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await getEvents(limit, 0);
        if (!cancelled) {
          setEvents(data.items);
          setTotal(data.total);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      }
    }

    poll();
    const id = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [limit]);

  return { events, total, error };
}