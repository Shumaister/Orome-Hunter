from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from core.models import Application

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "applications.json"

TRACKED_FIELDS = {"stage", "status"}


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_applications() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload.get("applications", [])


def save_applications(applications: list[dict]) -> None:
    _ensure_data_dir()
    payload = {"applications": applications}
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, DATA_FILE)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def create_application(data: dict) -> dict:
    if not data.get("company"):
        raise ValueError("company is required")
    if not data.get("role"):
        raise ValueError("role is required")

    application = Application(
        company=data["company"],
        role=data["role"],
        **{k: v for k, v in data.items() if k not in ("company", "role") and v is not None},
    )
    record = asdict(application)

    applications = load_applications()
    applications.append(record)
    save_applications(applications)
    return record


def _find(applications: list[dict], application_id: str) -> dict:
    for application in applications:
        if application["id"] == application_id:
            return application
    raise KeyError(f"No application with id {application_id}")


def update_application(application_id: str, changes: dict) -> dict:
    applications = load_applications()
    record = _find(applications, application_id)

    now = datetime.now().isoformat()
    for field, value in changes.items():
        record[field] = value
        if field in TRACKED_FIELDS:
            record["history"].append({"field": field, "value": value, "date": now})

    save_applications(applications)
    return record


def delete_application(application_id: str) -> None:
    applications = load_applications()
    remaining = [a for a in applications if a["id"] != application_id]
    if len(remaining) == len(applications):
        raise KeyError(f"No application with id {application_id}")
    save_applications(remaining)


def with_computed_fields(application: dict, today: date | None = None) -> dict:
    today = today or date.today()
    result = dict(application)
    app_date = date.fromisoformat(application["application_date"])
    result["days_since_application"] = (today - app_date).days
    return result


def list_applications(
    filters: dict | None = None,
    sort_by: str = "application_date",
    today: date | None = None,
) -> list[dict]:
    applications = [with_computed_fields(a, today=today) for a in load_applications()]

    filters = filters or {}
    for field, value in filters.items():
        if value is None:
            continue
        applications = [a for a in applications if a.get(field) == value]

    if sort_by == "days_since_application":
        applications.sort(key=lambda a: a["days_since_application"])
    else:
        applications.sort(key=lambda a: a["application_date"], reverse=True)

    return applications
