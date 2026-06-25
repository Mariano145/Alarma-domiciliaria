'use client';

/**
 * AlarmStateBadge — displays the current alarm state with color coding.
 *
 * Color mapping:
 *   DISARMED        → green
 *   ARMING_WAIT     → yellow (pulsing)
 *   ARMED_COUNTDOWN → blue
 *   ALARM           → red (pulsing)
 */

import { useAlarmState } from '@/hooks/useAlarmState';
import type { AlarmStateCode } from '@/types/alarm.types';

const STATE_STYLES: Record<AlarmStateCode, { bg: string; text: string; pulse: boolean }> = {
  DISARMED:        { bg: 'bg-green-100 border-green-400',  text: 'text-green-800',  pulse: false },
  ARMING_WAIT:     { bg: 'bg-yellow-100 border-yellow-400', text: 'text-yellow-800', pulse: true  },
  ARMED_COUNTDOWN: { bg: 'bg-blue-100 border-blue-400',    text: 'text-blue-800',   pulse: false },
  ALARM:           { bg: 'bg-red-100 border-red-500',      text: 'text-red-800',    pulse: true  },
};

const DOT_STYLES: Record<AlarmStateCode, string> = {
  DISARMED:        'bg-green-500',
  ARMING_WAIT:     'bg-yellow-500',
  ARMED_COUNTDOWN: 'bg-blue-500',
  ALARM:           'bg-red-500',
};

export function AlarmStateBadge() {
  const { state, error } = useAlarmState();

  if (error) {
    return (
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
        <p className="text-sm text-gray-500">No se puede conectar al backend.</p>
      </div>
    );
  }

  if (!state) {
    return (
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 animate-pulse">
        <div className="h-4 w-32 rounded bg-gray-200" />
      </div>
    );
  }

  const style = STATE_STYLES[state.stateCode];
  const dot   = DOT_STYLES[state.stateCode];

  return (
    <div className={`rounded-xl border-2 ${style.bg} p-5 flex flex-col gap-3`}>
      <div className="flex items-center gap-2">
        <span className={`inline-block size-3 rounded-full ${dot} ${style.pulse ? 'animate-pulse' : ''}`} />
        <span className={`text-xs font-semibold uppercase tracking-widest ${style.text}`}>
          Estado de alarma
        </span>
      </div>

      <p className={`text-2xl font-bold ${style.text}`}>
        {state.stateLabel}
      </p>

      <div className="flex flex-col gap-1 text-xs text-gray-500">
        <span>
          Actualizado:{' '}
          {new Date(state.updatedAt).toLocaleTimeString('es-AR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })}
        </span>
        {state.lastEventType && (
          <span>Último evento: <span className="font-mono">{state.lastEventType}</span></span>
        )}
      </div>
    </div>
  );
}