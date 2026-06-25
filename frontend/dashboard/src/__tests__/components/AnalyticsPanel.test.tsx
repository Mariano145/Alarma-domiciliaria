import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AnalyticsPanel } from '../../components/widgets/AnalyticsPanel';
import * as useAnalyticsModule from '../../hooks/useAnalytics';

vi.mock('../../hooks/useAnalytics');

describe('AnalyticsPanel', () => {
  it('shows loading skeleton when metrics is null', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: null,
      error: null,
    });

    const { container } = render(<AnalyticsPanel />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('shows error message when fetch fails', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: null,
      error: 'Network error',
    });

    render(<AnalyticsPanel />);
    expect(screen.getByText('No se pueden cargar métricas.')).toBeInTheDocument();
  });

  it('renders counts with labels', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: {
        counts: {
          doorOpens: 3,
          motionDetections: 5,
        },
        pinFailSuspicious: { active: false, activateAt: 3, deactivateAt: 1 },
        doorOpenAnomaly: { active: false, threshold: 6 },
      },
      error: null,
    });

    render(<AnalyticsPanel />);

    expect(screen.getByText('Eventos últimos 10 min')).toBeInTheDocument();
    expect(screen.getByText('Aperturas de puerta')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Movimiento')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('shows "Sin eventos recientes" when counts are empty', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: {
        counts: {},
        pinFailSuspicious: { active: false, activateAt: 3, deactivateAt: 1 },
        doorOpenAnomaly: { active: false, threshold: 6 },
      },
      error: null,
    });

    render(<AnalyticsPanel />);
    expect(screen.getByText('Sin eventos recientes.')).toBeInTheDocument();
  });

  it('shows PIN suspicious alert when active', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: {
        counts: {},
        pinFailSuspicious: { active: true, activateAt: 3, deactivateAt: 1 },
        doorOpenAnomaly: { active: false, threshold: 6 },
      },
      error: null,
    });

    render(<AnalyticsPanel />);
    expect(screen.getByText('PIN sospechoso')).toBeInTheDocument();
    expect(screen.getByText('⚠ Sí')).toBeInTheDocument();
  });

  it('shows PIN suspicious clear when not active', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: {
        counts: {},
        pinFailSuspicious: { active: false, activateAt: 3, deactivateAt: 1 },
        doorOpenAnomaly: { active: false, threshold: 6 },
      },
      error: null,
    });

    render(<AnalyticsPanel />);
    const noElements = screen.getAllByText('✓ No');
    expect(noElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows door anomaly alert when active', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: {
        counts: {},
        pinFailSuspicious: { active: false, activateAt: 3, deactivateAt: 1 },
        doorOpenAnomaly: { active: true, threshold: 6 },
      },
      error: null,
    });

    render(<AnalyticsPanel />);
    expect(screen.getByText('Anomalía puerta')).toBeInTheDocument();
    expect(screen.getByText('⚠ Sí')).toBeInTheDocument();
  });

  it('shows both alerts when both are active', () => {
    vi.mocked(useAnalyticsModule.useAnalytics).mockReturnValue({
      metrics: {
        counts: {},
        pinFailSuspicious: { active: true, activateAt: 3, deactivateAt: 1 },
        doorOpenAnomaly: { active: true, threshold: 6 },
      },
      error: null,
    });

    render(<AnalyticsPanel />);
    const alerts = screen.getAllByText('⚠ Sí');
    expect(alerts).toHaveLength(2);
  });
});
