import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useAlarmState } from '../../hooks/useAlarmState';
import * as alarmService from '../../services/alarm.service';

vi.mock('../../services/alarm.service');

describe('useAlarmState', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns null state and error initially', () => {
    vi.mocked(alarmService.getAlarmState).mockImplementation(
      () => new Promise(() => {}) // never resolves
    );

    const { result } = renderHook(() => useAlarmState());

    expect(result.current.state).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('fetches alarm state on mount', async () => {
    const mockState = {
      stateCode: 'DISARMED' as const,
      stateLabel: 'Desarmada',
      updatedAt: '2026-06-16T10:00:00Z',
      lastEventId: null,
      lastEventType: null,
    };

    vi.mocked(alarmService.getAlarmState).mockResolvedValueOnce(mockState);

    const { result } = renderHook(() => useAlarmState());

    await waitFor(() => {
      expect(result.current.state).toEqual(mockState);
    });

    expect(result.current.error).toBeNull();
    expect(alarmService.getAlarmState).toHaveBeenCalledTimes(1);
  });

  it('sets error when fetch fails', async () => {
    vi.mocked(alarmService.getAlarmState).mockRejectedValueOnce(
      new Error('Network error')
    );

    const { result } = renderHook(() => useAlarmState());

    await waitFor(() => {
      expect(result.current.error).toBe('Network error');
    });

    expect(result.current.state).toBeNull();
  });

  it('polls every 3 seconds', async () => {
    vi.useFakeTimers();

    const mockState1 = {
      stateCode: 'DISARMED' as const,
      stateLabel: 'Desarmada',
      updatedAt: '2026-06-16T10:00:00Z',
      lastEventId: null,
      lastEventType: null,
    };

    const mockState2 = {
      stateCode: 'ARMING_WAIT' as const,
      stateLabel: 'Armando...',
      updatedAt: '2026-06-16T10:00:03Z',
      lastEventId: 'evt-123',
      lastEventType: 'ARM_BUTTON_PRESSED',
    };

    vi.mocked(alarmService.getAlarmState)
      .mockResolvedValueOnce(mockState1)
      .mockResolvedValueOnce(mockState2);

    const { result } = renderHook(() => useAlarmState());

    // First fetch happens immediately
    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.state).toEqual(mockState1);

    // Advance 3 seconds to trigger second poll
    await act(async () => {
      await vi.advanceTimersByTimeAsync(3000);
    });

    expect(result.current.state).toEqual(mockState2);
    expect(alarmService.getAlarmState).toHaveBeenCalledTimes(2);

    vi.useRealTimers();
  });

  it('cleans up interval on unmount', () => {
    vi.useFakeTimers();

    vi.mocked(alarmService.getAlarmState).mockResolvedValue({
      stateCode: 'DISARMED' as const,
      stateLabel: 'Desarmada',
      updatedAt: '2026-06-16T10:00:00Z',
      lastEventId: null,
      lastEventType: null,
    });

    const { unmount } = renderHook(() => useAlarmState());

    expect(alarmService.getAlarmState).toHaveBeenCalledTimes(1);

    unmount();

    // Advance time after unmount - should not trigger more calls
    act(() => {
      vi.advanceTimersByTime(10000);
    });

    expect(alarmService.getAlarmState).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });
});
