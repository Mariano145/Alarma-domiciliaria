# Commit Message Convention

This document defines the strict commit message convention for our IoT project. All team members must adhere to this convention for every commit integrated into the development and main branches.

## 1. General Rule

Every commit message must follow this structure, based on Conventional Commits, with the strict condition that the **scope is mandatory**:

```
<type>(scope): <description>
empty line as separator
[optional body]
empty line as separator
[optional footer]
```

### 1.1 Structural Elements

* **`<type>`**: Describes the intent of the commit. Allowed types:
  * `feat`: A new feature for the user or system (e.g., a new endpoint, a new frontend view).
  * `fix`: A bug fix (e.g., fixing an algorithm edge case or a connection drop).
  * `docs`: Documentation changes only (e.g., updates to README, UML diagrams, or this file).
  * `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.).
  * `refactor`: A code change that neither fixes a bug nor adds a feature.
  * `test`: Adding missing tests or correcting existing tests (e.g., backend unit tests).
  * `chore`: Changes to the build process, auxiliary tools, or libraries (e.g., configuring linters, Git hooks, CI pipelines).
* **`(scope)`**: **[MANDATORY]** Provides additional contextual information about where the change took place (e.g., `backend`, `frontend`, `firmware`, `database`, `api`). It must always be enclosed in parentheses and cannot be omitted.
* **`<description>`**: A short, imperative summary of the code changes. It must include the corresponding **Jira issue key** (e.g., `IOT-123`) to ensure full traceability, followed by a brief text in English.
* **`[optional body]`**: Separated from the description by an empty line. Used to provide a more detailed explanatory text of the change, explaining the *what* and *why* behind the code.
* **`[optional footer]`**: Separated from the body (or description) by an empty line. Used mainly to reference breaking changes or block/close Jira issues.

---

## 2. Valid Examples

Here are three valid examples adhering strictly to the general rule, including the mandatory scope and the required Jira key.

### Example 1: New Feature (Backend)
```
feat(backend): IOT-34 implement strict telemetry payload validation

Add validation middleware to intercept incoming data from ESP32.
If the payload is malformed, returns a 400 Bad Request HTTP code 
and prevents any corrupt data from reaching the PostgreSQL database.
```

### Example 2: Bug Fix (Firmware)
```
fix(firmware): IOT-89 resolve bouncing issue on hardware button pin 12

Implement software debounce logic in the GPIO interrupt handler 
to prevent duplicate event triggers during physical testing.
```

### Example 3: Documentation Update (Architecture)
```
docs(architecture): IOT-12 merge initial UML class and sequence diagrams

Upload editable source files and exported images of the backend class diagram 
and the core data flow sequence diagrams into the docs/ directory.
```
