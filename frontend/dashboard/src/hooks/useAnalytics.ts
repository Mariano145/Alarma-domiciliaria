'use client';

import { useEffect, useState } from 'react';
import { getAnalytics } from '@/services/alarm.service';
import type { AnalyticsMetrics } from '@/types/alarm.types';

const POLL_INTERVAL_MS = 10000;

export function useAnalytics() {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function poll() {
      try {
        const data = await getAnalytics();
        if (!cancelled) { setMetrics(data); setError(null); }
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      }
    }
    poll();
    const id = setInterval(poll, POLL_INTERVAL_MS);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  return { metrics, error };
}