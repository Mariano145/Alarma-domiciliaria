# System Architecture — IoT Home Alarm

## 1. Context and Objective

The system is an IoT-based **home security alarm** that allows:
- Monitoring sensor events (door, motion, buttons, PIN keypad)
- Managing alarm states (disarmed, arming, armed, alarm triggered)
- Persisting event history in a database
- Visualizing real-time state and historical analysis from a web frontend
- Detecting anomalies through analysis algorithms

**Main actors:**
- **Home user** — Arms/disarms the alarm, checks status from the frontend
- **ESP32 (firmware)** — IoT device that captures sensor events and sends them to the backend
- **System auditor** — Queries history and analytics metrics

---

## 2. System Architecture: Distributed REST

The system follows a **distributed REST architecture** where components communicate exclusively via HTTP REST. Each component has its own internal architecture (see section 3 for backend details).

The system is composed of 4 main containers:

```
┌─────────────────┐
│   ESP32         │
│   (Firmware)    │
│   C++/Arduino   │
└────────┬────────┘
         │ HTTP POST /api/v1/events
         ▼
┌─────────────────────────────────────────┐
│   Backend (Flask + Python)              │
│   - Controllers (HTTP)                  │
│   - Services (business logic)           │
│   - Repositories (data access)          │
│   - Patterns: State, Strategy, Observer │
└────────┬────────────────────────────────┘
         │ SQL (SQLAlchemy)
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Database)    │
│   Table: events │
└─────────────────┘
         ▲
         │ HTTP GET (polling)
         │
┌────────┴────────┐
│   Frontend      │
│   React + TS    │
└─────────────────┘
```

**Data flow:**
1. ESP32 captures sensor events → sends to Backend via POST
2. Backend validates, persists in PostgreSQL, updates alarm state, notifies observers
3. Frontend polls Backend via GET to obtain current state, history, and analytics
4. Frontend renders real-time dashboards and historical tables

---

## 3. Layered Architecture (Backend)

The backend follows a classic **layered architecture** with separation of responsibilities:

### Layer 1: Controllers (HTTP)
**Responsibility:** Receive HTTP requests, validate parameters, delegate to services, return responses.

**Classes:**
- `EventController` — Event ingestion and query endpoints
- `AlarmController` — Current alarm state endpoint
- `AnalyticsController` — Computed metrics endpoint

**Does not contain:** business logic, direct DB access, complex validations.

### Layer 2: Services (Business Logic)
**Responsibility:** Orchestrate operations, apply business rules, manage state, notify observers.

**Classes:**
- `EventService` — Validates events, persists, notifies ingestion observers
- `AlarmStateManager` — Maintains current state, manages transitions (State pattern), notifies state observers
- `AnalyticsService` — Executes analytics algorithms (Strategy pattern)

**Does not contain:** HTTP logic, request serialization/deserialization.

### Layer 3: Repositories (Data Access)
**Responsibility:** Abstract PostgreSQL access, execute queries, map results to models.

**Classes:**
- `EventRepository` — Insert and query events with filters

**Does not contain:** business logic, domain validations.

### Layer 4: Models (Domain Entities)
**Responsibility:** Represent system entities as Python objects.

**Classes:**
- `Event` — Persisted event (eventId, type, deviceId, payload, receivedAt)
- `AlarmStateResponse` — Current alarm state
- `AnalyticsResponse` — Algorithm results

---

## 4. Design Patterns

The system uses 4 GoF patterns to solve specific architecture problems:

| Pattern | Problem it solves | Where it is applied |
|---------|-------------------|---------------------|
| **State** | The alarm has 4 states with different behaviors for the same events | `AlarmStateManager` + 4 concrete states |
| **Strategy** | We need 3 interchangeable analytics algorithms | `AnalyticsService` + 3 concrete strategies |
| **Observer #1** | Multiple components need to react when the alarm state changes | `AlarmStateManager` notifies `LiveStateCacheObserver`, `StateTransitionLoggerObserver` |
| **Observer #2** | Multiple components need to react when a new event arrives | `EventService` notifies `AnalyticsCacheInvalidatorObserver`, `EventStreamLoggerObserver` |

**See full details at:** [`design-patterns.md`](./design-patterns.md)

---

## 5. Architectural Decisions

### 5.1 Backend Framework: Flask
**Decision:** Use Flask as the single backend framework.

**Reasons:**
- Mature ecosystem with extensions for validation (Pydantic), DB (SQLAlchemy), migrations (Alembic)
- Team familiar with Python

**Alternatives considered:** NestJS (TypeScript), Spring Boot (Java).

### 5.2 Database: PostgreSQL
**Decision:** Use PostgreSQL as the relational database.

**Reasons:**
- Explicit requirement from the project brief
- Support in Flask via SQLAlchemy

### 5.3 Communication: REST HTTP
**Decision:** Use HTTP REST for ESP32<->Backend and Frontend<->Backend communication.

**Reasons:**
- Explicit requirement from the project brief

**Alternatives considered:** WebSockets — discarded due to additional complexity and because polling from the frontend is sufficient for the use case.

### 5.4 State Pattern for Alarm Management
**Decision:** Use the State pattern to model the alarm state machine.

**Reasons:**
- The alarm has 4 mutually exclusive states with different behaviors
- Each state encapsulates its own transition logic

**Alternatives considered:** Command (for requests), Factory (for creation), Decorator (for dynamic responsibilities) — discarded because they do not model mutually exclusive states.

### 5.5 Frontend: React with Polling
**Decision:** Use React and periodic polling to the backend for live updates.

**Reasons:**
- Explicit requirement from the project brief
- Polling is simple to implement and sufficient for real-time updates (2-5 second interval)
- Does not require additional infrastructure (WebSocket server)

**Alternatives considered:** WebSockets — discarded due to additional complexity for the project scope.

---

## 6. Constraints and Considerations

### Technical Constraints
- **Single backend:** The brief requires only one active backend framework in the final delivery
- **PostgreSQL mandatory:** The brief requires PostgreSQL for historical persistence
- **REST mandatory:** The brief requires REST for communication between components
- **Frontend cannot talk directly to ESP32:** Everything must go through the backend
- **Code in English:** All source code and technical comments must be in English
- **Documentation in Spanish:** Reports, Jira, and documentation may be in Spanish

### Design Considerations
- **Polling vs WebSockets:** Polling was chosen for simplicity.
- **Motion sensor:** Only triggers alarm in `ARMED_COUNTDOWN` state. In other states it is ignored to avoid false alarms when the user is at home.
- **Panic button:** Triggers alarm immediately regardless of current state (safety override).

---

## 7. References

- **Design patterns:** [`design-patterns.md`](./design-patterns.md)
- **API Contract (OpenAPI):** [`OpenAPI/openapi.yaml`](./OpenAPI/openapi.yaml)
- **Project brief:** [`CONSIGNA.md`](./CONSIGNA.md)
