import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EventsTable } from '../../components/widgets/EventsTable';
import * as useEventsModule from '../../hooks/useEvents';

vi.mock('../../hooks/useEvents');

describe('EventsTable', () => {
  it('shows error message when fetch fails', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [],
      total: 0,
      error: 'Network error',
    });

    render(<EventsTable />);
    expect(screen.getByText('No se puede conectar al backend.')).toBeInTheDocument();
  });

  it('shows empty state when no events', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [],
      total: 0,
      error: null,
    });

    render(<EventsTable />);
    expect(screen.getByText('Sin eventos registrados todavía.')).toBeInTheDocument();
  });

  it('renders event list with headers', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [
        {
          eventId: 'evt-12345678',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'DOOR_STATE_CHANGED',
          payload: { state: 'OPEN' },
        },
      ],
      total: 1,
      error: null,
    });

    render(<EventsTable />);

    expect(screen.getByText('Historial de eventos')).toBeInTheDocument();
    expect(screen.getByText('1 en total')).toBeInTheDocument();
    expect(screen.getByText('Tipo')).toBeInTheDocument();
    expect(screen.getByText('Detalle')).toBeInTheDocument();
    expect(screen.getByText('Dispositivo')).toBeInTheDocument();
    expect(screen.getByText('Recibido')).toBeInTheDocument();
  });

  it('renders DOOR_STATE_CHANGED event with state detail', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [
        {
          eventId: 'evt-12345678',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'DOOR_STATE_CHANGED',
          payload: { state: 'OPEN' },
        },
      ],
      total: 1,
      error: null,
    });

    render(<EventsTable />);

    expect(screen.getByText('Puerta')).toBeInTheDocument();
    expect(screen.getByText('OPEN')).toBeInTheDocument();
  });

  it('renders PIN_ATTEMPT SUCCESS with green text', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [
        {
          eventId: 'evt-12345678',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'PIN_ATTEMPT',
          payload: { result: 'SUCCESS' },
        },
      ],
      total: 1,
      error: null,
    });

    render(<EventsTable />);

    expect(screen.getByText('Intento de PIN')).toBeInTheDocument();
    expect(screen.getByText('Correcto')).toBeInTheDocument();
  });

  it('renders PIN_ATTEMPT FAIL with red text', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [
        {
          eventId: 'evt-12345678',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'PIN_ATTEMPT',
          payload: { result: 'FAIL' },
        },
      ],
      total: 1,
      error: null,
    });

    render(<EventsTable />);

    expect(screen.getByText('Incorrecto')).toBeInTheDocument();
  });

  it('renders multiple events', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [
        {
          eventId: 'evt-11111111',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'ARM_BUTTON_PRESSED',
          payload: {},
        },
        {
          eventId: 'evt-22222222',
          receivedAt: '2026-06-16T10:01:00Z',
          type: 'MOTION_DETECTED',
          payload: {},
        },
        {
          eventId: 'evt-33333333',
          receivedAt: '2026-06-16T10:02:00Z',
          type: 'PANIC_BUTTON_PRESSED',
          payload: {},
        },
      ],
      total: 3,
      error: null,
    });

    render(<EventsTable />);

    expect(screen.getByText('3 en total')).toBeInTheDocument();
    expect(screen.getByText('Botón armar')).toBeInTheDocument();
    expect(screen.getByText('Movimiento detectado')).toBeInTheDocument();
    expect(screen.getByText('Botón pánico')).toBeInTheDocument();
  });

  it('truncates eventId to 8 characters', () => {
    vi.mocked(useEventsModule.useEvents).mockReturnValue({
      events: [
        {
          eventId: 'evt-12345678-abcdef',
          receivedAt: '2026-06-16T10:00:00Z',
          type: 'MOTION_DETECTED',
          payload: {},
        },
      ],
      total: 1,
      error: null,
    });

    render(<EventsTable />);

    expect(screen.getByText('evt-1234…')).toBeInTheDocument();
  });
});
