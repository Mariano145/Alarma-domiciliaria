import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getAlarmState, getEvents, getAnalytics } from '../../services/alarm.service';

describe('alarm.service', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  describe('getAlarmState', () => {
    it('fetches alarm state from correct endpoint', async () => {
      const mockState = {
        stateCode: 'DISARMED',
        stateLabel: 'Desarmada',
        updatedAt: '2026-06-16T10:00:00Z',
        lastEventId: null,
        lastEventType: null,
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockState,
      } as Response);

      const result = await getAlarmState();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/v1/alarm/state',
        { cache: 'no-store' }
      );
      expect(result).toEqual(mockState);
    });

    it('throws error when fetch fails', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response);

      await expect(getAlarmState()).rejects.toThrow('Failed to fetch alarm state: 500');
    });
  });

  describe('getEvents', () => {
    it('fetches events with default pagination', async () => {
      const mockPage = {
        items: [],
        limit: 50,
        offset: 0,
        total: 0,
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPage,
      } as Response);

      const result = await getEvents();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/v1/events?limit=50&offset=0',
        { cache: 'no-store' }
      );
      expect(result).toEqual(mockPage);
    });

    it('fetches events with custom pagination', async () => {
      const mockPage = {
        items: [],
        limit: 10,
        offset: 20,
        total: 100,
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPage,
      } as Response);

      const result = await getEvents(10, 20);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/v1/events?limit=10&offset=20',
        { cache: 'no-store' }
      );
      expect(result).toEqual(mockPage);
    });

    it('throws error when fetch fails', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 404,
      } as Response);

      await expect(getEvents()).rejects.toThrow('Failed to fetch events: 404');
    });
  });

  describe('getAnalytics', () => {
    it('fetches analytics from correct endpoint', async () => {
      const mockMetrics = {
        windowMinutes: 10,
        counts: {
          doorOpens: 5,
          doorStateChanges: 10,
          pinFails: 2,
          panicPresses: 0,
          motionDetections: 3,
        },
        pinFailSuspicious: {
          active: false,
          activateAt: 3,
          deactivateAt: 1,
        },
        doorOpenAnomaly: {
          active: false,
          threshold: 6,
        },
        calculatedAt: '2026-06-16T10:00:00Z',
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetrics,
      } as Response);

      const result = await getAnalytics();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/v1/analytics',
        { cache: 'no-store' }
      );
      expect(result).toEqual(mockMetrics);
    });

    it('throws error when fetch fails', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 503,
      } as Response);

      await expect(getAnalytics()).rejects.toThrow('Failed to fetch analytics: 503');
    });
  });
});
