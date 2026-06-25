'use client';

/**
 * useAlarmState — polls GET /api/v1/alarm/state every 3 seconds.
 * Returns the current AlarmState and an error string if the fetch fails.
 */

import { useEffect, useState } from 'react';
import { getAlarmState } from '@/services/alarm.service';
import type { AlarmState } from '@/types/alarm.types';

const POLL_INTERVAL_MS = 3000;

export function useAlarmState() {
  const [state, setState] = useState<AlarmState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await getAlarmState();
        if (!cancelled) {
          setState(data);
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
  }, []);

  return { state, error };
}