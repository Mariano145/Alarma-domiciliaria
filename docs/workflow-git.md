# Git Workflow

This document defines the branch workflow that the team uses to develop the IoT project.

## 1. Branch Structure

The project follows a **Gitflow** model with three types of branches:

### 1.1 `master` (Production Branch)
- **Purpose:** Contains stable, functional code ready for delivery/evaluation.
- **Protection:** Only updated via approved Pull Requests (PR) from `develop`.
- **Rule:** Never commit directly to `master`.

### 1.2 `develop` (Integration Branch)
- **Purpose:** Continuous integration branch where all completed features are merged.
- **Usage:** The team merges their features here. It is the testing point before moving to `main`.
- **Rule:** Only updated via PRs from `feature/*` branches.

### 1.3 `feature/*` (Development Branches)
- **Purpose:** Each user story is developed in its own branch.
- **Origin:** Created from `develop`.
- **Destination:** Merged back to `develop` via PR.

---

## 2. Branch Naming

Every work branch must follow this format:

```
feature/IOT-XX-short-description
```

Where:
- `IOT-XX` = user story key in Jira
- `short-description` = brief description in lowercase and hyphens

### Valid examples:

```
feature/IOT-21-event-ingestion
feature/IOT-25-postgresql-persistence
feature/IOT-29-state-machine
feature/IOT-33-frontend-dashboard
feature/IOT-41-firmware-sensors
feature/IOT-45-analytics-algorithms
```

---

## 3. Step-by-Step Workflow

### Step 1: Create branch from develop

```bash
# Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# Create new branch for the story
git checkout -b feature/IOT-21-event-ingestion
```

### Step 2: Develop and commit

- Work on the `feature/*` branch
- Make frequent commits
- Follow the **commit convention** defined in `docs/commits-convention.md`

### Step 3: Update with develop before PR

```bash
# Bring changes from teammates who have already merged
git checkout develop
git pull origin develop
git checkout feature/IOT-21-event-ingestion
git merge develop
# Resolve conflicts if any
```

### Step 4: Create Pull Request

- Push the branch to the remote
- Create PR on GitHub targeting `develop`
- **PR title:** must include the Jira key (e.g., `IOT-21: Implement sensor event ingestion`)
- **Description:** mention what was implemented, which files were changed

### Step 5: Review and Approval

- **Minimum 2 approvals** from different team members (configured in GitHub)
- Review code, tests, linter, and compliance with the OpenAPI contract

### Step 6: Merge

- Once approved, merge to `develop`
- Delete the `feature/*` branch after merging

### Step 7: Move to main (when everything is integrated)

- When a set of features is stable on `develop`
- Create PR from `develop` to `main`
- Requires the same approvals

---

## 4. Merge Criteria

For a PR to be merged to `develop` or `main`:

1. **Approvals:** Minimum 2 approvals (or 1 if the team has 2 members)
2. **Tests:** All unit tests must pass (backend, frontend, firmware)
3. **Linter:** Code must pass the linter (`pre-commit`)
4. **CI/CD:** GitHub Actions must report successful checks (build + tests)
5. **Jira:** The PR must reference the user story key

## 6. Relationship Between Branches and Jira

| Element | Jira Linkage |
|---------|-------------|
| **Branch** | `feature/IOT-XX` -> story IOT-XX in Jira |
| **Commit** | `feat(backend): IOT-XX implements...` -> key IOT-XX |
| **PR** | Title: `IOT-XX: feature description` |
| **Merge** | When merging, Jira can detect the PR and update the story |

---

## 7. Visual Summary

```
        ┌─────────────────────────────────────────────────────────┐
        │                    main (protected)                     │
        │              Stable code, evaluation                    │
        └─────────────────────────────────────────────────────────┘
                              ↑  PR with 2 approvals
                              │  + tests passing
                              │
        ┌─────────────────────────────────────────────────────────┐
        │                  develop (protected)                    │
        │           Integration of all features                   │
        └─────────────────────────────────────────────────────────┘
           ↑                    ↑                    ↑
           │ PR 2 approvals     │ PR 2 approvals     │ PR 2 approvals
           │                    │                    │
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ feature/IOT- │    │ feature/IOT- │    │ feature/IOT- │
    │    21        │    │    25        │    │    29        │
    └──────────────┘    └──────────────┘    └──────────────┘
```

## 9. Notes for the Team

- **Never** commit directly to `main` or `develop`
- **Always** create a `feature/*` branch from an up-to-date `develop`
- **Always** include the Jira key in commits and PRs
- **Review** other team members' PRs before approving: code, tests, linter, documentation
- **Update** Jira when a subtask is finished (move to "Done")
