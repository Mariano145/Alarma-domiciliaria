#!/usr/bin/env python3
"""
Emulate ESP32 sensor events for testing the deployed backend.
Sends random events every 3 seconds to simulate a real alarm system.
"""

import random
import time
import requests

BACKEND_URL = "https://backend-alarma-domiciliaria-production.up.railway.app"
EVENTS_ENDPOINT = f"{BACKEND_URL}/api/v1/events"

EVENT_TYPES = [
    {"type": "DOOR_STATE_CHANGED", "payload": {"state": random.choice(["OPEN", "CLOSED"])}},
    {"type": "MOTION_DETECTED", "payload": {}},
    {"type": "PIN_ATTEMPT", "payload": {"result": random.choice(["SUCCESS", "FAIL"])}},
    {"type": "ARM_BUTTON_PRESSED", "payload": {}},
    {"type": "PANIC_BUTTON_PRESSED", "payload": {}},
]

def send_event():
    event = random.choice(EVENT_TYPES)
    event["deviceId"] = "esp32-alarma"
    
    try:
        response = requests.post(EVENTS_ENDPOINT, json=event, timeout=5)
        if response.status_code == 201:
            print(f"✓ Sent: {event['type']}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print(f"Sending events to {BACKEND_URL} every 3 seconds...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            send_event()
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nStopped.")
