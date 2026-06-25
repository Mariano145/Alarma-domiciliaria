import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useAnalytics } from '../../hooks/useAnalytics';
import * as alarmService from '../../services/alarm.service';

vi.mock('../../services/alarm.service');

describe('useAnalytics', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns null metrics and error initially', () => {
    vi.mocked(alarmService.getAnalytics).mockImplementation(
      () => new Promise(() => {})
    );

    const { result } = renderHook(() => useAnalytics());

    expect(result.current.metrics).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('fetches analytics on mount', async () => {
    const mockMetrics = {
      counts: { doorOpens: 2 },
      pinFailSuspicious: { active: false, activateAt: 3, deactivateAt: 1 },
      doorOpenAnomaly: { active: false, threshold: 6 },
    };

    vi.mocked(alarmService.getAnalytics).mockResolvedValueOnce(mockMetrics);

    const { result } = renderHook(() => useAnalytics());

    await waitFor(() => {
      expect(result.current.metrics).toEqual(mockMetrics);
    });

    expect(result.current.error).toBeNull();
  });

  it('sets error when fetch fails', async () => {
    vi.mocked(alarmService.getAnalytics).mockRejectedValueOnce(
      new Error('Server error')
    );

    const { result } = renderHook(() => useAnalytics());

    await waitFor(() => {
      expect(result.current.error).toBe('Server error');
    });

    expect(result.current.metrics).toBeNull();
  });

  it('polls every 10 seconds', async () => {
    vi.useFakeTimers();

    const mockMetrics1 = {
      counts: { motionDetections: 1 },
      pinFailSuspicious: { active: false, activateAt: 3, deactivateAt: 1 },
      doorOpenAnomaly: { active: false, threshold: 6 },
    };

    const mockMetrics2 = {
      counts: { motionDetections: 3 },
      pinFailSuspicious: { active: true, activateAt: 3, deactivateAt: 1 },
      doorOpenAnomaly: { active: false, threshold: 6 },
    };

    vi.mocked(alarmService.getAnalytics)
      .mockResolvedValueOnce(mockMetrics1)
      .mockResolvedValueOnce(mockMetrics2);

    const { result } = renderHook(() => useAnalytics());

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.metrics).toEqual(mockMetrics1);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(10000);
    });

    expect(result.current.metrics).toEqual(mockMetrics2);
    expect(alarmService.getAnalytics).toHaveBeenCalledTimes(2);

    vi.useRealTimers();
  });

  it('cleans up interval on unmount', () => {
    vi.useFakeTimers();

    vi.mocked(alarmService.getAnalytics).mockResolvedValue({
      counts: {},
      pinFailSuspicious: { active: false, activateAt: 3, deactivateAt: 1 },
      doorOpenAnomaly: { active: false, threshold: 6 },
    });

    const { unmount } = renderHook(() => useAnalytics());

    expect(alarmService.getAnalytics).toHaveBeenCalledTimes(1);

    unmount();

    act(() => {
      vi.advanceTimersByTime(20000);
    });

    expect(alarmService.getAnalytics).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });
});
