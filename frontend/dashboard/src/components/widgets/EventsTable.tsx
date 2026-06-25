'use client';

/**
 * EventsTable — displays the alarm event history with polling.
 * Uses useEvents hook for live updates every 5 seconds.
 */

import { useEvents } from '@/hooks/useEvents';
import type { AlarmEvent, EventType } from '@/types/alarm.types';

const EVENT_LABELS: Record<EventType, string> = {
  ARM_BUTTON_PRESSED:   'Botón armar',
  PANIC_BUTTON_PRESSED: 'Botón pánico',
  DOOR_STATE_CHANGED:   'Puerta',
  PIN_ATTEMPT:          'Intento de PIN',
  MOTION_DETECTED:      'Movimiento detectado',
  ARMING_TIMEOUT:       'Timeout de armado',
  ENTRY_TIMEOUT:        'Timeout de entrada',
};

const EVENT_COLORS: Record<EventType, string> = {
  ARM_BUTTON_PRESSED:   'bg-blue-100 text-blue-700',
  PANIC_BUTTON_PRESSED: 'bg-red-100 text-red-700',
  DOOR_STATE_CHANGED:   'bg-yellow-100 text-yellow-700',
  PIN_ATTEMPT:          'bg-purple-100 text-purple-700',
  MOTION_DETECTED:      'bg-orange-100 text-orange-700',
  ARMING_TIMEOUT:       'bg-gray-100 text-gray-700',
  ENTRY_TIMEOUT:        'bg-gray-100 text-gray-700',
};

function PayloadCell({ event }: { event: AlarmEvent }) {
  const p = event.payload;
  if (event.type === 'DOOR_STATE_CHANGED') return <span>{String(p.state)}</span>;
  if (event.type === 'PIN_ATTEMPT') {
    const ok = p.result === 'SUCCESS';
    return (
      <span className={ok ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
        {ok ? 'Correcto' : 'Incorrecto'}
      </span>
    );
  }
  return <span className="text-gray-400">—</span>;
}

export function EventsTable() {
  const { events, total, error } = useEvents(50);

  if (error) {
    return <p className="text-sm text-gray-500 py-4">No se puede conectar al backend.</p>;
  }

  if (events.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-gray-300 p-8 text-center text-sm text-gray-400">
        Sin eventos registrados todavía.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-700">Historial de eventos</h2>
        <span className="text-xs text-gray-400">{total} en total</span>
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              <th className="px-4 py-3">Tipo</th>
              <th className="px-4 py-3">Detalle</th>
              <th className="px-4 py-3">Dispositivo</th>
              <th className="px-4 py-3">Recibido</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {events.map((event) => (
              <tr key={event.eventId} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${EVENT_COLORS[event.type]}`}>
                    {EVENT_LABELS[event.type] ?? event.type}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">
                  <PayloadCell event={event} />
                </td>
                <td className="px-4 py-3 font-mono text-xs text-gray-500">
                  {event.eventId.slice(0, 8)}…
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {new Date(event.receivedAt).toLocaleString('es-AR', {
                    day: '2-digit',
                    month: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}