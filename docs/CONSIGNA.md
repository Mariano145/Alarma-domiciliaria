# Project Brief — Final IoT Project

**Universidad Nacional de Cordoba** · Facultad de Ciencias Exactas, Fisicas y Naturales · Software Engineering

This document defines the **obligations** and **acceptance criteria** for the final project. The **functional and non-functional requirements** are defined by **the team** (Jira, `docs/`, course deliverables, etc.) with the freedom of form and granularity appropriate, as long as the result is **compatible** with everything required here: this brief acts as a **set of constraints**.

---

## Quick Summary

| Scope | What is required |
|-------|-----------------|
| Process | **Jira on the web** with a **new team project**; PRs mandatory for story work; **minimum 2 approvals** per PR; each commit integrated with **story key** (`KEY-NNN`); **even code contribution**; **documented Git workflow** ([Gitflow — Atlassian](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) recommended); **documented commit convention** ([Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.4/) recommended); **pre-commit** and **pre-push** **hooks** installable by the team; **linter** in repo and executed in **pre-commit** (no need to repeat lint in Actions) |
| ESP32 | Collection of environmental events (buttons, sensors, potentiometers, keypads, etc.); **>=3 distinct channels or modalities** in the demo |
| Backend | **Single framework** chosen by the team; **>=3 distinct algorithms** on persisted data or tied to PostgreSQL; consistent validation and HTTP codes |
| Data | Everything entering from the ESP32 must be **saved in historical storage** in **PostgreSQL** |
| Integration | **REST** between ESP32<->backend and frontend<->backend; the **frontend cannot** call the ESP32 **directly** |
| Contracts | API agreed upon and **documented beforehand** (e.g. OpenAPI in the repo) |
| Frontend | **Historical query** (tables or other structured format) and **live visualization** of sensors and algorithm outputs (charts, text, or tables at the team's discretion) |
| Patterns | **Observer** mandatory (**>=2** concrete structures); **Strategy** mandatory; **>=1 third GoF pattern** chosen by the team, justified in writing |
| Reactivity | Must not use **only** `useState` (or other local reactive state) as the sole mechanism for propagating domain data: relevant updates **must pass** through the defined Observer abstractions |
| Language | **Code and comments in English**; reports and Jira may be in Spanish |
| GitHub Actions | Only **GitHub Actions**: **`.github/workflows/`**; on **PRs** to integration: at minimum **build + unit tests** for the chosen **backend**; **frontend:** **build + unit tests**; **firmware:** **`pio test`** (PlatformIO unit tests). **Not** required to run the **linter** again in the pipeline (**pre-commit** is sufficient). Required jobs / branch protection documented |
| Testing | **Backend, frontend and firmware:** only **unit tests**; integration/API tests are **valued** in the backend. **Test** commands must match across **GitHub Actions**, **pre-push**, and local documentation |
| UML Design (before code) | **Before** implementing substantive functionality: **(1)** **component** diagram (architecture); **(2)** **class** diagram at least for the **backend**; **(3)** **one or more** **sequence** diagrams for relevant flows. Source + exported view in `docs/` |

---

# 1. Product Requirements

## 1.1 General Scope

The team must develop a functional IoT system composed of:

* **ESP32 firmware**,
* a **backend**,
* a **PostgreSQL database**,
* and a **frontend**.

The system must be demonstrable end-to-end in a functional demo.

**Acceptance criterion:** during the final evaluation, the complete flow **ESP32 -> backend -> PostgreSQL -> frontend** must be observable.

---

## 1.2 Minimum Acquisition from ESP32

The ESP32 firmware must capture information from **at least three distinct input modalities** from the environment or human interaction.

Distinct modalities include, for example:

* button,
* analog sensor,
* digital sensor,
* potentiometer,
* matrix keypad,
* encoder,
* switch,
* distance sensor,
* temperature sensor.

Three sensors of the same type without a clear functional difference do not count as distinct modalities.

**Acceptance criterion:** during the demo, **three distinct modalities** generating events or measurements that effectively enter the system must be observed.

---

## 1.3 Historical Persistence

Every event, telemetry, or data accepted by the backend from the ESP32 must be persisted in **PostgreSQL** and remain available for subsequent queries, even when the device is powered off or disconnected.

**Acceptance criterion:** after disconnecting the ESP32, the frontend or a query tool can retrieve previously stored data.

---

## 1.4 Frontend: Historical Data and Live Visualization

The frontend must provide:

* at least one **historical query** view in structured format (table, tabular list, grid, or other equivalent format),
* and at least one **live update** view of:

  * data from sensors or inputs,
  * and results generated by backend algorithms.

Live updates must occur **without requiring a manual browser refresh**.

**Acceptance criterion:** during the demo, historical data can be queried and new updates can be observed in the interface without manually reloading the page.

---

# 2. Architecture and Technical Requirements

## 2.1 Integration Between Components

Communication between components must follow these rules:

* **ESP32 <-> backend:** via documented HTTP REST.
* **Frontend <-> backend:** via documented HTTP REST.
* The **frontend cannot communicate directly with the ESP32** to access domain data.

For live visualization, the team may implement polling or another equivalent mechanism to/from the backend, as long as the frontend does not consume data directly from the device.

**Acceptance criterion:** code review, configuration, and observable traffic show that the browser consumes data only from the backend.

---

## 2.2 Single Backend

The team must select **a single backend framework** for the evaluated delivery. It should not be necessary to run multiple alternative backends for the system to work in the demo.

**Acceptance criterion:** execution documentation and the demo use a single active backend as part of the evaluated product.

---

## 2.3 API Contract Before Consumption

Endpoints used by firmware and frontend must be defined in a **versioned contract** within the repository before being consumed by those clients.

OpenAPI or another equivalent REST format is accepted, as long as it documents at least:

* path,
* HTTP method,
* expected payload,
* expected response,
* relevant error codes.

### Operational Definition of "Before Coding" in This Context

A contract is considered published **before consumption** if the repository shows that the endpoint definition was incorporated before the first commit or PR that:

* invokes that endpoint from frontend or firmware,
* depends on its fields,
* or implements client logic coupled to that contract.

The following cases are not considered contract "consumption":

* initial scaffolding,
* isolated temporary mocks,
* exploratory tests not integrated into the main flow,
* empty project structure.

**Acceptance criterion:** in the Git history, the contract definition appears before the first integrated use of each endpoint by frontend or firmware.

---

## 2.4 Backend Algorithms

The backend must implement **at least three distinct algorithms** applied to data ingested, persisted, or queried from PostgreSQL.

### Operational Definition of "Distinct Algorithm"

For this brief, two algorithms are considered distinct if they simultaneously meet these conditions:

1. they perform a **different transformation, analysis, or decision** on the data,
2. they produce a **semantically different output** or pursue a different purpose,
3. they are implemented as separable units of code,
4. they can be identified and explained separately in documentation or API.

Valid examples:

* moving average,
* moving median,
* Kalman filter,
* threshold with hysteresis,
* anomaly detection,
* temporal window aggregation,
* state classification.

Examples that do **not** count as distinct algorithms on their own:

* changing a threshold constant,
* the same logic with a different name,
* the same operation applied to three different sensors,
* three trivial variants without a clear functional difference.

Each algorithm must be linked to the real system flow, reading persisted data, processing it, or generating results that the system exposes or uses.

**Acceptance criterion:** in the repository and/or API, three algorithms can be identified with name, purpose, differentiable inputs and outputs, and an explicit link to PostgreSQL usage.

---

## 2.5 Backend Validation and Minimum Quality

The backend must validate ingestion payloads and respond with consistent HTTP codes.

In case of an invalid payload, the backend must:

* respond with a **4xx** code,
* and **not persist** invalid or corrupt records.

**Acceptance criterion:** a manual test with a malformed payload generates a 4xx response and does not leave garbage persisted.

---

# 3. Design and Modeling Requirements

## 3.1 Mandatory UML Before Substantive Development

Before implementing substantive system functionality, the team must version in `docs/`:

1. a **component diagram**,
2. a **class diagram** of the backend,
3. one or more **sequence diagrams** of relevant flows.

The **editable source** of the diagram must also be included and, if the tool allows it, an exported readable version.

### Operational Definition of "Before Coding"

For the purposes of this brief, **substantive development** is considered to be any of the following:

* implementation of domain logic,
* creation of real endpoints,
* real database persistence,
* ESP32 <-> backend integration,
* frontend <-> backend integration,
* implementation of system algorithms,
* implementation of business or UI flows tied to the final product.

The following are not considered substantive development:

* repository creation,
* initial project configuration,
* scaffolding,
* dependency installation,
* linter, hook, or CI configuration,
* placeholder files,
* disposable proof-of-concept tests not integrated into the main flow.

**Acceptance criterion:** diagrams must be merged in the repository before the first PR or set of commits that introduces substantive development according to this definition.

---

## 3.2 Consistency Between Design and Final System

The UML design does not have to match the final code line by line, but it must reasonably reflect the architecture and central flows of the delivered system.

**Acceptance criterion:** the component diagram matches the real components; the class diagram represents the effectively implemented backend; and at least one sequence diagram covers a real end-to-end system flow.

---

## 3.3 Design Patterns

The system must demonstrate:

* at least **two concrete implementations** of the **Observer** pattern,
* at least one implementation of the **Strategy** pattern,
* and at least **one third GoF pattern**, justified in writing in `docs/`.

### Observer

The two concrete Observer implementations must correspond to two distinguishable system flows or structures.
Simply duplicating names or empty classes is not sufficient.

### Strategy

A Strategy is considered valid if there are at least **two real interchangeable strategies** used by the system to solve the same problem.

### Third GoF Pattern

It must be explicitly identified:

* pattern name,
* classes or modules fulfilling each role,
* justification of why it was used.

**Acceptance criterion:** the code and documentation allow clear identification of the implementations and roles of the three patterns.

---

# 4. Process Requirements

## 4.1 Jira

The team must use **Jira web** with a team project for this course, unless otherwise indicated by the teaching staff.

There must be:

* identifiable project,
* backlog with user stories,
* associated tasks,
* work tracking.

The repository must include:

* project name,
* URL,
* key prefix.

**Acceptance criterion:** the project exists, has visible stories and tasks, and the repository references it unambiguously.

---

## 4.2 Pull Requests and Reviews

All work tied to user stories must be integrated via **pull request** to a protected integration branch.

Each PR must:

* reference the corresponding Jira key,
* have at least **two approvals** from different team members before merging.

If the team has only **two members**, the minimum required is **one approval** from the other person.

**Acceptance criterion:** repository configuration and PR history show compliance with this rule.

---

## 4.3 Balanced Contribution

Team participation must be auditable and distributed.

Balanced contribution will be considered if, unless documented justification exists, **each member** meets at least two of these conditions throughout the term:

* participates as author of integrated PRs,
* performs approving reviews,
* contributes substantive commits,
* has assigned and closed tasks in Jira,
* appears linked to relevant system components or stories.

Balance will not be evaluated solely by commit count.

**Acceptance criterion:** the combined evidence from Git, PRs, and Jira allows verification of effective participation from all members.

---

## 4.4 Documented Git Workflow

The team must define, document, and follow a branch workflow in `docs/`.

The documentation must indicate at least:

* work branches,
* integration branch,
* PR integration method,
* merge criteria,
* relationship between branches and Jira.

**Acceptance criterion:** the document exists and the actual repository usage matches what is documented.

---

## 4.5 Commit Convention

The team must use a single commit message convention and document it in `docs/`.

The documentation must include:

* general rule,
* at least three valid examples,
* inclusion of Jira key in each example.

**Acceptance criterion:** the convention is documented and recent integrated commits consistently follow it.

---

# 5. Quality and Automation Requirements

## 5.1 Language

The following must be in **English**:

* source code,
* comments,
* internal API names,
* relevant identifiers.

The following may be in Spanish:

* team documentation,
* Jira,
* reports,
* non-technical external texts if the product requires it.

**Acceptance criterion:** in the integration branch, no comments or technical API names appear in Spanish, except user-visible strings when appropriate.

---

## 5.2 Testing

**Unit tests** must exist for:

* backend,
* frontend,
* firmware.

Tests must:

* be versioned in the repo,
* be executable locally,
* match the commands used in CI,
* cover relevant system logic.

Integration tests in the backend are valued but not mandatory.

**Acceptance criterion:** visible tests exist in all three components and their commands are documented and aligned with CI.

---

## 5.3 GitHub Actions

CI automation must be implemented exclusively with **GitHub Actions** in `.github/workflows/`.

On PRs to the integration branch, the following must run automatically at minimum:

* **backend:** build + unit tests,
* **frontend:** build + unit tests,
* **firmware:** `pio test`.

**Acceptance criterion:** a PR to integration shows successful or failed automatic checks for those three scopes.

---

## 5.4 Git Hooks

The repository must allow installing and using:

* `pre-commit`, which runs at least the linter,
* `pre-push`, which runs at least the required tests or an equivalent documented verification.

Hooks must be versioned or installable from the repository itself.

**Acceptance criterion:** documentation allows activating hooks on a clean clone and the team can demonstrate their functioning.

---

## 5.5 Linter

At least one linter must be configured and versioned for each active component of the delivered system:

* backend,
* frontend,
* firmware.

The linter must run in `pre-commit`.

**Acceptance criterion:** linter configuration files exist in the repo and the `pre-commit` hook invokes it.

---

# 6. Minimum Required Evidence for Evaluation

To consider the delivery complete, observable evidence of all the following points must exist:

1. functional demo **ESP32 -> backend -> PostgreSQL -> frontend**,
2. three distinct input modalities from ESP32,
3. historical persistence in PostgreSQL,
4. frontend with historical data and live updates without manual refresh,
5. a single active backend,
6. versioned API contract before consumption,
7. three distinct correctly identifiable algorithms,
8. mandatory UML diagrams versioned before substantive development,
9. two Observers, one Strategy, and one third GoF pattern identifiable,
10. Jira project with stories and tasks,
11. PRs with minimum required approvals,
12. documented Git workflow,
13. documented commit convention,
14. code and technical comments in English,
15. unit tests in backend, frontend, and firmware,
16. GitHub Actions running on PRs,
17. installable hooks,
18. linter configured and executed in pre-commit.

---

# 7. Final Notes

The product RFs and RNFs are still defined by the team, but they cannot contradict any of the constraints in this brief.

In case of interpretation doubts, the following criteria will always prevail:

* **observable evidence in the repository**,
* **traceability in Git/Jira**,
* and **demonstrability during evaluation**.


### Nice to have — Docker Compose in Actions (production-like environment)

When the project is **sufficiently advanced or closed**, the team **may** add an optional job in GitHub Actions that:

- runs **`docker compose build`** to build the **images** from the `Dockerfile` / manifests in the repo,
- brings up the stack with **`docker compose up`** (or an appropriate variant for CI: minimum profile, `depends_on` + healthchecks, "simulated prod" environment variables),

as a **smoke test** of the integrated deployment (backend, database, frontend in containers, depending on what the team has dockerized), approaching a **production-like environment**.

It must be **documented** in `docs/` or **ABOUT** how to reproduce the same flow on a local machine. It is **not** a course approval requirement unless the instructor indicates otherwise separately.

---

For installation and base repository stack, see [ABOUT.md](../ABOUT.md).
