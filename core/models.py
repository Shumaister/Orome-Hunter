from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class WorkMode(str, Enum):
    HYBRID = "Hybrid"
    REMOTE = "Remote"


class Status(str, Enum):
    ON_HOLD = "On hold"
    ACTIVE = "Active"
    OFFER = "Offer"
    REJECTED = "Rejected"
    CLOSED = "Closed"
    WITHDRAWN = "Withdrawn"


class Stage(str, Enum):
    APPLICATION = "Application"
    RECRUITER = "Recruiter"
    HR_INTERVIEW = "HR Interview"
    TECHNICAL_INTERVIEW = "Technical Interview"
    CLIENT_INTERVIEW = "Client Interview"
    FINAL_INTERVIEW = "Final Interview"
    OFFER = "Offer"
    CLOSED = "Closed"


@dataclass
class HistoryEntry:
    field: str
    value: str
    date: str


@dataclass
class Application:
    company: str
    role: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: str = Priority.MEDIUM.value
    source: str = ""
    link: str = ""
    work_mode: str = ""
    location: str = ""
    application_date: str = field(default_factory=lambda: date.today().isoformat())
    resume_used: str = ""
    desired_salary: str = ""
    status: str = Status.ACTIVE.value
    stage: str = Stage.APPLICATION.value
    recruiter: str = ""
    last_contact: str | None = None
    next_step: str = ""
    next_step_date: str | None = None
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    history: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.history:
            now = self.created_at
            self.history = [
                {"field": "stage", "value": self.stage, "date": now},
                {"field": "status", "value": self.status, "date": now},
            ]
