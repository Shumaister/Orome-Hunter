# Plan 001: Application Tracker

**Related spec:** [spec.md](./spec.md)

## Technical decisions

- **Language:** Python.
- **Persistence:** a single local JSON file (`data/applications.json`), gitignored. No database, no external server. If data volume ever justifies it, we migrate (see constitution, principle 4) — not designing for that now.
- **Interface:** local web app with [Streamlit](https://streamlit.io/), running on `localhost` via `streamlit run app.py`. Gives an editable table, forms, and filters without writing separate HTML/JS — the simplest option for a single user.
- **No auth, no deploy:** the only "server" is the Streamlit process on your machine.

## Folder structure

```
orome-hunter/
├── app.py                    # Streamlit entrypoint (UI)
├── core/
│   ├── __init__.py
│   ├── models.py              # Application dataclass, Priority/WorkMode/Status/Stage enums
│   └── storage.py             # JSON load/save, CRUD, change history
├── data/
│   └── applications.json      # gitignored, created on first use
├── specs/
│   ├── constitution.md
│   └── 001-tracker-postulaciones/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── tests/
│   └── test_storage.py
└── requirements.txt
```

## Data model (JSON)

Each application is an object inside a root list. Structure:

```json
{
  "applications": [
    {
      "id": "uuid4-string",
      "priority": "Medium",
      "company": "Acme Corp",
      "role": "Backend Engineer",
      "source": "LinkedIn",
      "link": "https://...",
      "work_mode": "Remote",
      "location": "Buenos Aires, AR",
      "application_date": "2026-08-19",
      "resume_used": "Resume_Backend_v3",
      "desired_salary": "USD 3000",
      "status": "Active",
      "stage": "Application",
      "recruiter": "",
      "last_contact": null,
      "next_step": "",
      "next_step_date": null,
      "notes": "",
      "created_at": "2026-08-19T14:32:00",
      "history": [
        {"field": "stage", "value": "Application", "date": "2026-08-19T14:32:00"},
        {"field": "status", "value": "Active", "date": "2026-08-19T14:32:00"}
      ]
    }
  ]
}
```

- `id`: UUID4, generated at creation. The key used to edit/delete.
- `history`: append-only list of changes to `stage` and `status` (H3). Every field change adds an entry; nothing is ever overwritten. This is what will feed analytics (spec 003).
- `days_since_application` is **not stored**: it's computed on read, in `core/storage.py` or the UI, as `today - application_date`.
- Atomic writes: on save, write to a temp file and rename over `applications.json`, so the file never gets corrupted if the process dies mid-write.

## Layers and responsibilities

- **`core/models.py`**: defines the shape of an Application and the closed enums (Priority, WorkMode, Status, Stage), so validation doesn't depend on loose strings scattered through the code.
- **`core/storage.py`**: the only layer that touches the JSON file.
  - `load_applications() -> list[Application]`
  - `save_applications(list[Application]) -> None`
  - `create_application(data) -> Application`
  - `update_application(id, changes) -> Application` (if `changes` touches `stage` or `status`, appends to `history`)
  - `delete_application(id) -> None`
  - `list_applications(filters) -> list[Application]`
- **`app.py`**: UI only. Calls `core/storage.py`, never reads/writes the JSON directly. Uses `st.data_editor` or table + form for H1/H2/H4, selects to change Stage/Status (H3), text fields for follow-up (H5).

Keeping `core` separate from `app.py`, even for a small project, is what lets us later reuse `core/storage.py` from a future CLI or from the analytics spec (003) without duplicating logic.

## Out of scope for this plan

- Everything the spec marks out of scope (auth, notifications, automatic import, attachments, analytics, job-offer search).
- Exhaustive UI tests — Streamlit is tested manually; unit tests for `core/storage.py` (CRUD and days-since calculation) are worthwhile.

## Next step

`tasks.md` with the concrete, ordered list of implementation tasks.
