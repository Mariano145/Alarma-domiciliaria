'use client';

import { useAnalytics } from '@/hooks/useAnalytics';

const LABEL: Record<string, string> = {
  doorOpens:        'Aperturas de puerta',
  doorStateChanges: 'Cambios de estado puerta',
  pinFails:         'Intentos de PIN fallidos',
  panicPresses:     'Botón pánico',
  motionDetections: 'Movimiento',
};

export function AnalyticsPanel() {
  const { metrics, error } = useAnalytics();

  if (error) return <p className="text-sm text-gray-500">No se pueden cargar métricas.</p>;
  if (!metrics) return <div className="animate-pulse h-24 rounded-xl bg-gray-100" />;

  const counts = Object.entries(metrics.counts);

  return (
    <div className="flex flex-col gap-4">
      {/* Windowed counts */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
          Eventos últimos 10 min
        </p>
        {counts.length === 0 ? (
          <p className="text-xs text-gray-400">Sin eventos recientes.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {counts.map(([type, count]) => (
              <li key={type} className="flex items-center justify-between text-sm">
                <span className="text-gray-600">{LABEL[type] ?? type}</span>
                <span className="font-bold text-gray-900">{count}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Alertas */}
      <div className="grid grid-cols-2 gap-3">
        <div className={`rounded-xl border p-4 ${metrics.pinFailSuspicious.active ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-white'}`}>
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">PIN sospechoso</p>
          <p className={`mt-1 text-xl font-bold ${metrics.pinFailSuspicious.active ? 'text-red-700' : 'text-green-700'}`}>
            {metrics.pinFailSuspicious.active ? '⚠ Sí' : '✓ No'}
          </p>
        </div>
        <div className={`rounded-xl border p-4 ${metrics.doorOpenAnomaly.active ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-white'}`}>
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">Anomalía puerta</p>
          <p className={`mt-1 text-xl font-bold ${metrics.doorOpenAnomaly.active ? 'text-red-700' : 'text-green-700'}`}>
            {metrics.doorOpenAnomaly.active ? '⚠ Sí' : '✓ No'}
          </p>
        </div>
      </div>
    </div>
  );
}