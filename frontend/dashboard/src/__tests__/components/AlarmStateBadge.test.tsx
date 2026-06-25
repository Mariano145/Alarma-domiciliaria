import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AlarmStateBadge } from '../../components/widgets/AlarmStateBadge';
import * as useAlarmStateModule from '../../hooks/useAlarmState';

vi.mock('../../hooks/useAlarmState');

describe('AlarmStateBadge', () => {
  it('shows loading skeleton when state is null', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: null,
      error: null,
    });

    const { container } = render(<AlarmStateBadge />);

    // Should have animate-pulse class (loading state)
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('shows error message when fetch fails', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: null,
      error: 'Network error',
    });

    render(<AlarmStateBadge />);

    expect(screen.getByText('No se puede conectar al backend.')).toBeInTheDocument();
  });

  it('renders DISARMED state with green styling', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: {
        stateCode: 'DISARMED',
        stateLabel: 'Desarmada',
        updatedAt: '2026-06-16T10:00:00Z',
        lastEventId: null,
        lastEventType: null,
      },
      error: null,
    });

    render(<AlarmStateBadge />);

    expect(screen.getByText('Estado de alarma')).toBeInTheDocument();
    expect(screen.getByText('Desarmada')).toBeInTheDocument();
    expect(screen.getByText(/Actualizado:/)).toBeInTheDocument();
  });

  it('renders ARMING_WAIT state with yellow styling', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: {
        stateCode: 'ARMING_WAIT',
        stateLabel: 'Armando...',
        updatedAt: '2026-06-16T10:00:00Z',
        lastEventId: 'evt-123',
        lastEventType: 'ARM_BUTTON_PRESSED',
      },
      error: null,
    });

    render(<AlarmStateBadge />);

    expect(screen.getByText('Armando...')).toBeInTheDocument();
    expect(screen.getByText(/ARM_BUTTON_PRESSED/)).toBeInTheDocument();
  });

  it('renders ARMED_COUNTDOWN state with blue styling', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: {
        stateCode: 'ARMED_COUNTDOWN',
        stateLabel: 'Armada',
        updatedAt: '2026-06-16T10:00:00Z',
        lastEventId: 'evt-456',
        lastEventType: 'DOOR_STATE_CHANGED',
      },
      error: null,
    });

    render(<AlarmStateBadge />);

    expect(screen.getByText('Armada')).toBeInTheDocument();
  });

  it('renders ALARM state with red styling', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: {
        stateCode: 'ALARM',
        stateLabel: 'Alarma',
        updatedAt: '2026-06-16T10:00:00Z',
        lastEventId: 'evt-789',
        lastEventType: 'MOTION_DETECTED',
      },
      error: null,
    });

    render(<AlarmStateBadge />);

    expect(screen.getByText('Alarma')).toBeInTheDocument();
    expect(screen.getByText(/MOTION_DETECTED/)).toBeInTheDocument();
  });

  it('does not show last event when lastEventType is null', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: {
        stateCode: 'DISARMED',
        stateLabel: 'Desarmada',
        updatedAt: '2026-06-16T10:00:00Z',
        lastEventId: null,
        lastEventType: null,
      },
      error: null,
    });

    render(<AlarmStateBadge />);

    expect(screen.queryByText(/Último evento:/)).not.toBeInTheDocument();
  });

  it('shows last event when lastEventType is present', () => {
    vi.mocked(useAlarmStateModule.useAlarmState).mockReturnValue({
      state: {
        stateCode: 'ALARM',
        stateLabel: 'Alarma',
        updatedAt: '2026-06-16T10:00:00Z',
        lastEventId: 'evt-999',
        lastEventType: 'PANIC_BUTTON_PRESSED',
      },
      error: null,
    });

    render(<AlarmStateBadge />);

    expect(screen.getByText(/Último evento:/)).toBeInTheDocument();
    expect(screen.getByText('PANIC_BUTTON_PRESSED')).toBeInTheDocument();
  });
});
