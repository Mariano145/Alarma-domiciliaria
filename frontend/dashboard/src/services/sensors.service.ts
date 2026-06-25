/**
 * This is the only file allowed to call fetch() for sensor-related API access.
 *
 * Uses `process.env.NEXT_PUBLIC_API_URL` from the monorepo root `.env` (see root `.env.example`).
 *
 * Students must implement:
 * - `getLatestReadings()` — fetch recent readings for the dashboard
 * - `getReadingsBySensor(sensorId)` — filter readings for one sensor
 * - `getAlerts()` — fetch alert payloads for widgets
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

/**
 * 1. Fetches the most recent readings for the general dashboard.
 * Consumes the historical events endpoint, sorted by timestamp DESC by default.
 */
export async function getLatestReadings(limit: number = 50) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/events?limit=${limit}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Error in getLatestReadings: ${response.statusText}`);
    }

    const data = await response.json();
    return data.items; // Returns the list of EventItem according to the EventPage schema
  } catch (error) {
    console.error(error);
    return [];
  }
}

/**
 * 2. Filters readings for a specific sensor type using the API 'type' query parameter.
 * Note: The OpenAPI spec filters by `type` (e.g., 'DOOR_STATE_CHANGED', 'MOTION_DETECTED', etc.)
 */
export async function getReadingsBySensor(sensorType: string, limit: number = 50) {
  try {
    const url = new URL(`${API_BASE_URL}/api/v1/events`);
    url.searchParams.append('type', sensorType);
    url.searchParams.append('limit', limit.toString());

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Error in getReadingsBySensor: ${response.statusText}`);
    }

    const data = await response.json();
    return data.items;
  } catch (error) {
    console.error(error);
    return [];
  }
}

/**
 * 3. Fetches active alerts processed by the backend analytics algorithms.
 * Consumes the analytics endpoint and maps the active anomalies for the frontend widgets.
 */
export async function getAlerts() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Error in getAlerts: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Maps the response targeting the 'active' state of each backend anomaly detector
    return {
      pinFailSuspicious: data.pinFailSuspicious.active,
      doorOpenAnomaly: data.doorOpenAnomaly.active,
      calculatedAt: data.calculatedAt,
      counts: data.counts
    };
  } catch (error) {
    console.error(error);
    // UI strings like error messages
    return {
      pinFailSuspicious: false,
      doorOpenAnomaly: false,
      calculatedAt: new Date().toISOString(),
      counts: { doorOpens: 0, doorStateChanges: 0, pinFails: 0, panicPresses: 0, motionDetections: 0 },
      errorMessage: "No se pudieron cargar las alertas en este momento" 
    };
  }
}
