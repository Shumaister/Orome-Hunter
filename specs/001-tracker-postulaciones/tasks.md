# Tasks 001: Application Tracker

**Related plan:** [plan.md](./plan.md)

Ordered, small, independently verifiable tasks. Each references the user story (spec.md) it implements. Do them in order — later tasks depend on earlier ones.

Per constitution principles 7–8: tests are never run without asking first, and every task below is tagged **testable** or **not testable** so effort isn't spent testing things that don't add value.

## Phase 0 — Project setup

- **T001. Scaffold folders and files** _(not testable — trivial setup)_
  Create `core/`, `core/__init__.py`, `data/`, `tests/`, empty `core/models.py`, `core/storage.py`, `app.py`, `requirements.txt`.
  *Verify:* structure matches `plan.md`, `data/` is gitignored (already done).

- **T002. Dependencies** _(not testable — trivial setup)_
  Add `streamlit` and `pytest` to `requirements.txt`. Install into a virtualenv.
  *Verify:* `pip install -r requirements.txt` succeeds; `streamlit hello` or `python -c "import streamlit"` works.

## Phase 1 — Core data layer (no UI yet)

- **T003. Define enums and Application shape (`core/models.py`)** _(not testable on its own — default-filling behavior is covered by T005's tests)_
  `Priority` (High/Medium/Low), `WorkMode` (Hybrid/Remote), `Status` (On hold/Active/Offer/Rejected/Closed/Withdrawn), `Stage` (Application/Recruiter/HR Interview/Technical Interview/Client Interview/Final Interview/Offer/Closed). A dataclass or TypedDict `Application` with every field from the spec's data model table, plus `id`, `created_at`, `history`.
  *Verify:* importing the module works; instantiating an `Application` with only required fields (company, role) fills the rest with the documented defaults.

- **T004. JSON load/save with atomic writes (`core/storage.py`)** _(testable)_
  `load_applications()` returns `[]` if the file doesn't exist yet (first run). `save_applications(list)` writes to a temp file and renames over `data/applications.json`.
  *Verify (unit test):* save then load round-trips the same data; killing/interrupting a save never leaves a half-written `applications.json` (temp+rename covers this by construction).

- **T005. Create/list/update/delete (`core/storage.py`)** — implements H1, H2, H4 _(testable)_
  `create_application(data)`, `list_applications(filters=None)`, `update_application(id, changes)`, `delete_application(id)`.
  *Verify (unit tests):* creating with only company+role sets status=Active, stage=Application, application_date=today; updating a non-`stage`/`status` field doesn't touch `history`; deleting removes the record and its history.

- **T006. History tracking on stage/status change (`core/storage.py`)** — implements H3 _(testable)_
  When `update_application` changes `stage` or `status`, append `{field, value, date}` to `history` instead of just overwriting.
  *Verify (unit test):* two consecutive stage changes produce two ordered history entries, in addition to the initial one from creation.

- **T007. Computed `days_since_application`** — implements H2 _(testable)_
  A function (e.g. `with_computed_fields(application)`) that adds `days_since_application = today - application_date` without persisting it.
  *Verify (unit test):* the value updates correctly across a mocked "today"; the stored JSON never contains this key.

- **T008. Filtering and sorting in `list_applications`** — implements H2 _(testable)_
  Support filtering by `status`, `stage`, `priority`; sorting by `application_date` (default, most recent first) and by `days_since_application`.
  *Verify (unit tests):* filter combinations return the expected subset; default order is most-recent-first.

## Phase 2 — UI (Streamlit, `app.py`)

- **T009. Read-only table view** — implements H2 _(not testable — UI, covered by manual smoke test T015)_
  Render all applications via `st.dataframe`/`st.data_editor`, columns: company, role, priority, status, stage, days_since_application.
  *Verify:* `streamlit run app.py` shows existing data (start with an empty file — confirms T004's first-run behavior too).

- **T010. Filters and sorting controls** — implements H2 _(not testable — UI, covered by manual smoke test T015)_
  Add `st.selectbox`/`st.multiselect` for status/stage/priority filters and a sort control, wired to T008.
  *Verify:* changing a filter updates the visible rows without a full page reload glitching state.

- **T011. Create-application form** — implements H1 _(not testable — UI, covered by manual smoke test T015)_
  A form (`st.form`) with all fields from the data model; required fields enforced (company, role); submits via `create_application`.
  *Verify:* submitting with only company+role creates a row with correct defaults; submitting without company or role is rejected with a visible message.

- **T012. Edit / update stage & status / delete** — implements H3, H4 _(not testable — UI, covered by manual smoke test T015)_
  Select a row (e.g. via `st.selectbox` of company+role, or `st.data_editor` inline edit) to edit any field, change stage/status specifically, or delete it with a confirmation step.
  *Verify:* editing a field persists after re-running the app; changing stage or status appears in that application's `history`; delete removes it from the table.

- **T013. Follow-up fields** — implements H5 _(not testable — UI, covered by manual smoke test T015)_
  Expose recruiter, last_contact, next_step, next_step_date, notes as editable fields (can reuse T012's edit flow).
  *Verify:* entering/updating these fields persists and survives an app reload.

## Phase 3 — Wrap-up

- **T014. Automated tests for the core logic (`tests/test_storage.py`)** _(this task writes and runs tests — will ask before executing `pytest`, per constitution principle 7)_
  A small, focused pytest suite for `core/storage.py` only — the key logic, not exhaustive coverage. One test per behavior already called out as "Verify (unit test)" in T004–T008: atomic save/load round-trip, create fills correct defaults, updating a non-stage/status field leaves `history` untouched, stage/status changes append to `history` in order, delete removes the record and its history, `days_since_application` computes correctly and is never persisted, filter/sort combinations return the expected subset. The Streamlit UI itself stays out of this suite — it's covered by the manual smoke test below (see plan.md's scope note).
  *Verify:* `pytest` passes; every "Verify (unit test)" note from T004–T008 has a matching test function.

- **T015. Smoke test the full flow manually** _(manual, not automated — this is what covers all the UI tasks marked not testable above)_
  Create 3–4 realistic applications, move them through different stages/statuses, edit one, delete one, restart `streamlit run` and confirm everything persisted.
  *Verify:* matches every acceptance criterion in `spec.md` H1–H5.

- **T016. Update repo README** _(not testable — documentation)_
  Replace the placeholder README with a short description of what the tool does and how to run it (`pip install -r requirements.txt`, `streamlit run app.py`).
  *Verify:* a stranger could get it running from the README alone.
