from __future__ import annotations

from datetime import date

import pytest

from core import storage


@pytest.fixture(autouse=True)
def isolated_data_file(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "DATA_FILE", tmp_path / "applications.json")
    yield


def test_load_applications_returns_empty_list_when_file_missing():
    assert storage.load_applications() == []


def test_save_then_load_roundtrips_data():
    records = [{"id": "1", "company": "Acme"}]
    storage.save_applications(records)
    assert storage.load_applications() == records


def test_create_application_fills_defaults():
    record = storage.create_application({"company": "Acme", "role": "Backend Engineer"})
    assert record["status"] == "Active"
    assert record["stage"] == "Application"
    assert record["application_date"] == date.today().isoformat()


def test_create_application_requires_company_and_role():
    with pytest.raises(ValueError):
        storage.create_application({"company": "Acme"})
    with pytest.raises(ValueError):
        storage.create_application({"role": "Backend Engineer"})


def test_update_non_tracked_field_does_not_touch_history():
    record = storage.create_application({"company": "Acme", "role": "Backend Engineer"})
    history_before = len(record["history"])

    updated = storage.update_application(record["id"], {"notes": "Great chat with recruiter"})

    assert updated["notes"] == "Great chat with recruiter"
    assert len(updated["history"]) == history_before


def test_stage_and_status_changes_append_ordered_history():
    record = storage.create_application({"company": "Acme", "role": "Backend Engineer"})

    storage.update_application(record["id"], {"stage": "Recruiter"})
    updated = storage.update_application(record["id"], {"status": "On hold"})

    fields_in_order = [entry["field"] for entry in updated["history"]]
    assert fields_in_order == ["stage", "status", "stage", "status"]
    assert updated["history"][-2]["value"] == "Recruiter"
    assert updated["history"][-1]["value"] == "On hold"


def test_delete_application_removes_record_and_history():
    record = storage.create_application({"company": "Acme", "role": "Backend Engineer"})

    storage.delete_application(record["id"])

    assert storage.load_applications() == []


def test_delete_unknown_application_raises():
    with pytest.raises(KeyError):
        storage.delete_application("does-not-exist")


def test_days_since_application_is_computed_not_persisted():
    record = storage.create_application(
        {"company": "Acme", "role": "Backend Engineer", "application_date": "2026-08-10"}
    )

    listed = storage.list_applications(today=date(2026, 8, 19))
    assert listed[0]["days_since_application"] == 9

    raw = storage.load_applications()
    assert "days_since_application" not in raw[0]


def test_filters_return_expected_subset():
    storage.create_application({"company": "Acme", "role": "Backend", "status": "Active"})
    storage.create_application({"company": "Globex", "role": "Frontend", "status": "Rejected"})

    active_only = storage.list_applications(filters={"status": "Active"})

    assert len(active_only) == 1
    assert active_only[0]["company"] == "Acme"


def test_default_sort_is_most_recent_application_first():
    storage.create_application({"company": "Old", "role": "A", "application_date": "2026-01-01"})
    storage.create_application({"company": "New", "role": "B", "application_date": "2026-08-01"})

    result = storage.list_applications()

    assert [a["company"] for a in result] == ["New", "Old"]
