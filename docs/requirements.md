# System Requirements — IoT Alarm Project

This document specifies the functional requirements (FR) and non-functional requirements (NFR) of the IoT alarm system.

---

## Functional Requirements (FR)

**FR-01:** The system shall allow activating the alarm via the physical arm button.

**FR-02:** The system shall allow deactivating the alarm via correct PIN entry on the matrix keypad.

**FR-03:** The system shall record door opening events detected by the ESP32.

**FR-04:** The system shall record motion events detected by the PIR sensor.

**FR-05:** The system shall record panic button activations.

**FR-06:** The system shall display the history of recorded events in tabular format.

**FR-07:** The system shall display the current alarm state in real time.

**FR-08:** The system shall execute analysis algorithms on stored events (Windowed Counts, PIN Fail Suspicious, Door Open Anomaly).

**FR-09:** The system shall display the results of the analysis algorithms on the dashboard in a structured format.

**FR-10:** The interface shall update without requiring manual refresh.

---

## Non-Functional Requirements (NFR)

**NFR-01:** The system must use a PostgreSQL relational database for historical storage.

**NFR-02:** The frontend and ESP32 must communicate with the backend exclusively via HTTP REST.

**NFR-03:** The backend must be implemented using a single development framework (Flask).

**NFR-04:** The backend must validate input JSON. If a payload is invalid, it must respond with HTTP 4xx code and abort persistence to the database.

**NFR-05:** All source code, API identifiers, and comments must be strictly in English.

**NFR-06:** The ESP32 firmware must include automated unit tests executable via the `pio test` command in GitHub Actions.

**NFR-07:** Domain data propagation to the live frontend must not rely solely on local state (useState), but must be channeled through Observer pattern abstractions.

**NFR-08:** In case of physical disconnection of the ESP32 or frontend crash, previously accepted data must remain intact and accessible in PostgreSQL for subsequent audits.

**NFR-09:** The backend must implement at least three distinct algorithms on data persisted in PostgreSQL, with semantically differentiated and separately identifiable outputs.

**NFR-10:** The system must demonstrate: at least two concrete implementations of the Observer pattern, at least one implementation of the Strategy pattern, and at least one third GoF pattern (State) with written justification.

**NFR-11:** The repository must include GitHub Actions in `.github/workflows/` that execute build + unit tests for backend, frontend, and firmware (`pio test`) on every Pull Request.

**NFR-12:** The repository must allow installing `pre-commit` (linter) and `pre-push` (tests) hooks, versioned or installable from the repository itself.

**NFR-13:** Before implementing substantive functionality, the team must version in `docs/` a component diagram, a backend class diagram, and one or more sequence diagrams of relevant flows.

**NFR-14:** The team must use a single commit message convention, documented in `docs/`, including a general rule, at least three valid examples, and Jira key in each example.
