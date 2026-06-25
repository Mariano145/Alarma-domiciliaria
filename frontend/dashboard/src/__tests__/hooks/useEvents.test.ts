import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useEvents } from '../../hooks/useEvents';
import * as alarmService from '../../services/alarm.service';

vi.mock('../../services/alarm.service');

describe('useEvents', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns empty events and zero total initially', () => {
    vi.mocked(alarmService.getEvents).mockImplementation(
      () => new Promise(() => {})
    );

    const { result } = renderHook(() => useEvents());

    expect(result.current.events).toEqual([]);
    expect(result.current.total).toBe(0);
    expect(result.current.error).toBeNull();
  });

  it('fetches events on mount with default limit', async () => {
    const mockPage = {
      items: [
        {
          eventId: 'evt-001',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'DOOR_STATE_CHANGED' as const,
          payload: { state: 'OPEN' },
        },
      ],
      limit: 50,
      offset: 0,
      total: 1,
    };

    vi.mocked(alarmService.getEvents).mockResolvedValueOnce(mockPage);

    const { result } = renderHook(() => useEvents());

    await waitFor(() => {
      expect(result.current.events).toEqual(mockPage.items);
      expect(result.current.total).toBe(1);
    });

    expect(alarmService.getEvents).toHaveBeenCalledWith(50, 0);
  });

  it('fetches events with custom limit', async () => {
    const mockPage = {
      items: [],
      limit: 10,
      offset: 0,
      total: 0,
    };

    vi.mocked(alarmService.getEvents).mockResolvedValueOnce(mockPage);

    const { result } = renderHook(() => useEvents(10));

    await waitFor(() => {
      expect(result.current.events).toEqual([]);
    });

    expect(alarmService.getEvents).toHaveBeenCalledWith(10, 0);
  });

  it('sets error when fetch fails', async () => {
    vi.mocked(alarmService.getEvents).mockRejectedValueOnce(
      new Error('Connection refused')
    );

    const { result } = renderHook(() => useEvents());

    await waitFor(() => {
      expect(result.current.error).toBe('Connection refused');
    });

    expect(result.current.events).toEqual([]);
    expect(result.current.total).toBe(0);
  });

  it('polls every 5 seconds', async () => {
    vi.useFakeTimers();

    const mockPage1 = {
      items: [
        {
          eventId: 'evt-001',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'ARM_BUTTON_PRESSED' as const,
          payload: {},
        },
      ],
      limit: 50,
      offset: 0,
      total: 1,
    };

    const mockPage2 = {
      items: [
        {
          eventId: 'evt-001',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'ARM_BUTTON_PRESSED' as const,
          payload: {},
        },
        {
          eventId: 'evt-002',
          receivedAt: '2026-06-16T10:00:05Z',
          type: 'MOTION_DETECTED' as const,
          payload: {},
        },
      ],
      limit: 50,
      offset: 0,
      total: 2,
    };

    vi.mocked(alarmService.getEvents)
      .mockResolvedValueOnce(mockPage1)
      .mockResolvedValueOnce(mockPage2);

    const { result } = renderHook(() => useEvents());

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.total).toBe(1);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5000);
    });

    expect(result.current.total).toBe(2);
    expect(result.current.events).toHaveLength(2);
    expect(alarmService.getEvents).toHaveBeenCalledTimes(2);

    vi.useRealTimers();
  });

  it('cleans up interval on unmount', () => {
    vi.useFakeTimers();

    vi.mocked(alarmService.getEvents).mockResolvedValue({
      items: [],
      limit: 50,
      offset: 0,
      total: 0,
    });

    const { unmount } = renderHook(() => useEvents());

    expect(alarmService.getEvents).toHaveBeenCalledTimes(1);

    unmount();

    act(() => {
      vi.advanceTimersByTime(15000);
    });

    expect(alarmService.getEvents).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });

  it('re-fetches when limit changes', async () => {
    const mockPage1 = {
      items: [],
      limit: 50,
      offset: 0,
      total: 0,
    };

    const mockPage2 = {
      items: [],
      limit: 10,
      offset: 0,
      total: 0,
    };

    vi.mocked(alarmService.getEvents)
      .mockResolvedValueOnce(mockPage1)
      .mockResolvedValueOnce(mockPage2);

    const { rerender } = renderHook(
      ({ limit }) => useEvents(limit),
      { initialProps: { limit: 50 } }
    );

    await waitFor(() => {
      expect(alarmService.getEvents).toHaveBeenCalledWith(50, 0);
    });

    rerender({ limit: 10 });

    await waitFor(() => {
      expect(alarmService.getEvents).toHaveBeenCalledWith(10, 0);
    });
  });
});
