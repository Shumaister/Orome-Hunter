# Orome Hunter

A personal, local-only tracker for job applications. Register each application, move it through stages (recruiter screen, interviews, offer...), track status, and keep notes and follow-ups, without depending on a spreadsheet or memory.

It's a single-user tool: no accounts, no server, no cloud — everything runs and stays on your own machine.

## Development approach

This project is built with **Spec-Driven Development (SDD)**. Nothing gets coded before it's been through this flow:

1. **Constitution** ([specs/constitution.md](specs/constitution.md)) — the non-negotiable principles behind every decision in the project.
2. **Spec** (`specs/<number>-<name>/spec.md`) — WHAT is being built and WHY, in plain user-story language. No frameworks, no databases, no code.
3. **Plan** (`plan.md`) — HOW: the technical decisions and architecture for that spec.
4. **Tasks** (`tasks.md`) — the ordered, small, independently verifiable steps derived from the plan.
5. **Implementation** — only after the above exists.

See [specs/](specs/) for the full history of what's been decided and why. Current status:

| Spec | What | Status |
|---|---|---|
| 001 | Application tracker | Implemented |
| 002 | Job-offer search/aggregator | Pending (depends on 001) |
| 003 | Personal analytics | Pending (depends on 001) |

## Technical infrastructure

- **Language:** Python.
- **UI:** [Streamlit](https://streamlit.io/), served locally on `localhost` — no deployment, no external hosting.
- **Persistence:** a single local JSON file, `data/applications.json` (gitignored). No database, no server-side storage. Writes are atomic (temp file + rename) so the file can't get corrupted mid-save.
- **Testing:** `pytest`, focused only on the core data logic (`core/storage.py`) — CRUD, change history, filtering/sorting. The UI is verified manually, not through automated tests (see the relevant `tasks.md` for the reasoning).
- **Structure:**
  - `app.py` — the Streamlit UI: table, filters, sorting, create/edit/delete, history view.
  - `core/models.py` — data shapes and enums (Priority, Status, Stage, Work Mode).
  - `core/storage.py` — the only module that touches the JSON file: load/save, CRUD, history tracking, computed fields.
  - `tests/` — automated tests for `core/storage.py`.
  - `specs/` — the constitution and every spec/plan/tasks set, in numbered order.

## Run it

```
pip install -r requirements.txt
streamlit run app.py
```

Data is stored locally in `data/applications.json` (gitignored) — nothing leaves your machine.
