/**
 * TypeScript interfaces matching the backend API response shapes
 * for alarm state and event history.
 */

export type AlarmStateCode =
  | 'DISARMED'
  | 'ARMING_WAIT'
  | 'ARMED_COUNTDOWN'
  | 'ALARM';

export interface AlarmState {
  stateCode: AlarmStateCode;
  stateLabel: string;
  updatedAt: string;
  lastEventId: string | null;
  lastEventType: string | null;
}

export type EventType =
  | 'ARM_BUTTON_PRESSED'
  | 'PANIC_BUTTON_PRESSED'
  | 'DOOR_STATE_CHANGED'
  | 'PIN_ATTEMPT'
  | 'MOTION_DETECTED'
  | 'ARMING_TIMEOUT'
  | 'ENTRY_TIMEOUT';

export interface AlarmEvent {
  eventId: string;
  receivedAt: string;
  type: EventType;
  payload: Record<string, unknown>;
}

export interface EventPage {
  items: AlarmEvent[];
  limit: number;
  offset: number;
  total: number;
}

/** Props for alarm components */
export interface AlarmStateBadgeProps {
  state: AlarmState;
}

export interface EventsTableProps {
  events: AlarmEvent[];
  total: number;
}

export interface AnalyticsMetrics {
  counts: Record<string, number>;
  pinFailSuspicious: { active: boolean; activateAt: number; deactivateAt: number };
  doorOpenAnomaly: { active: boolean; threshold: number };
}