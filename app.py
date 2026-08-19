from __future__ import annotations

import pandas as pd
import streamlit as st

from core.models import Priority, Stage, Status, WorkMode
from core.storage import create_application, delete_application, list_applications, update_application

st.set_page_config(page_title="Orome Hunter", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 100%; }
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
    button[kind="secondary"] { border-color: #D4D4D8; }
    button[kind="primary"] { background-color: #16A34A; border-color: #16A34A; color: #FFFFFF; }
    button[kind="primary"]:hover { background-color: #15803D; border-color: #15803D; color: #FFFFFF; }
    </style>
    """,
    unsafe_allow_html=True,
)

PRIORITY_COLORS = {
    Priority.HIGH.value: "#FECACA",
    Priority.MEDIUM.value: "#FEF3C7",
    Priority.LOW.value: "#DCFCE7",
}

STATUS_COLORS = {
    Status.ON_HOLD.value: "#FEF3C7",
    Status.ACTIVE.value: "#DBEAFE",
    Status.OFFER.value: "#DCFCE7",
    Status.REJECTED.value: "#FEE2E2",
    Status.CLOSED.value: "#E4E4E7",
    Status.WITHDRAWN.value: "#FFEDD5",
}

STAGE_COLORS = {
    Stage.APPLICATION.value: "#F4F4F5",
    Stage.RECRUITER.value: "#E0E7FF",
    Stage.HR_INTERVIEW.value: "#C7D2FE",
    Stage.TECHNICAL_INTERVIEW.value: "#A5B4FC",
    Stage.CLIENT_INTERVIEW.value: "#93C5FD",
    Stage.FINAL_INTERVIEW.value: "#7DD3FC",
    Stage.OFFER.value: "#86EFAC",
    Stage.CLOSED.value: "#D4D4D8",
}

ZEBRA_COLORS = ("#FFFFFF", "#F4F4F5")


def style_table(df: pd.DataFrame) -> "pd.io.formats.style.Styler":
    def style_row(row: pd.Series) -> list[str]:
        zebra = ZEBRA_COLORS[row.name % 2]
        colors = {col: zebra for col in df.columns}
        if "priority" in colors:
            colors["priority"] = PRIORITY_COLORS.get(row["priority"], zebra)
        if "status" in colors:
            colors["status"] = STATUS_COLORS.get(row["status"], zebra)
        if "stage" in colors:
            colors["stage"] = STAGE_COLORS.get(row["stage"], zebra)
        return [f"background-color: {colors[col]}" for col in df.columns]

    return df.style.apply(style_row, axis=1)

COLUMNS = [
    ("priority", "Priority"),
    ("company", "Company"),
    ("role", "Role"),
    ("source", "Source"),
    ("link", "Link"),
    ("work_mode", "Work Mode"),
    ("location", "Location"),
    ("application_date", "Application Date"),
    ("resume_used", "Resume Used"),
    ("desired_salary", "Desired Salary"),
    ("status", "Status"),
    ("stage", "Stage"),
    ("recruiter", "Recruiter"),
    ("last_contact", "Last Contact"),
    ("next_step", "Next Step"),
    ("next_step_date", "Next Step Date"),
    ("days_since_application", "Days Since Application"),
    ("notes", "Notes"),
    ("history_summary", "History"),
]

if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "filters" not in st.session_state:
    st.session_state.filters = {"status": None, "stage": None, "priority": None}
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "application_date"


# --- Dialogs ---

@st.dialog("Add application")
def add_dialog() -> None:
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company *")
        role = st.text_input("Role *")
        priority = st.selectbox("Priority", [p.value for p in Priority], index=1)
        source = st.text_input("Source")
        link = st.text_input("Link")
        work_mode = st.selectbox("Work mode", [""] + [m.value for m in WorkMode])
        location = st.text_input("Location")
    with col2:
        resume_used = st.text_input("Resume used")
        desired_salary = st.text_input("Desired salary")
        recruiter = st.text_input("Recruiter")
        next_step = st.text_input("Next step")
        next_step_date = st.text_input("Next step date (YYYY-MM-DD)")
        notes = st.text_area("Notes")

    if st.button("Add", icon=":material/check:", type="primary"):
        if not company or not role:
            st.error("Company and Role are required.")
        else:
            create_application(
                {
                    "company": company,
                    "role": role,
                    "priority": priority,
                    "source": source,
                    "link": link,
                    "work_mode": work_mode,
                    "location": location,
                    "resume_used": resume_used,
                    "desired_salary": desired_salary,
                    "recruiter": recruiter,
                    "next_step": next_step,
                    "next_step_date": next_step_date or None,
                    "notes": notes,
                }
            )
            st.rerun()


@st.dialog("Filter")
def filter_dialog() -> None:
    status = st.selectbox(
        "Status", ["(all)"] + [s.value for s in Status],
        index=(["(all)"] + [s.value for s in Status]).index(st.session_state.filters["status"] or "(all)"),
    )
    stage = st.selectbox(
        "Stage", ["(all)"] + [s.value for s in Stage],
        index=(["(all)"] + [s.value for s in Stage]).index(st.session_state.filters["stage"] or "(all)"),
    )
    priority = st.selectbox(
        "Priority", ["(all)"] + [p.value for p in Priority],
        index=(["(all)"] + [p.value for p in Priority]).index(st.session_state.filters["priority"] or "(all)"),
    )
    if st.button("Apply", icon=":material/check:"):
        st.session_state.filters = {
            "status": None if status == "(all)" else status,
            "stage": None if stage == "(all)" else stage,
            "priority": None if priority == "(all)" else priority,
        }
        st.rerun()
    if st.button("Clear filters"):
        st.session_state.filters = {"status": None, "stage": None, "priority": None}
        st.rerun()


@st.dialog("Sort")
def sort_dialog() -> None:
    options = {"Application date (newest first)": "application_date", "Days since application": "days_since_application"}
    label = st.radio("Sort by", list(options.keys()))
    if st.button("Apply", icon=":material/check:"):
        st.session_state.sort_by = options[label]
        st.rerun()


@st.dialog("History")
def history_dialog(application: dict) -> None:
    st.write(f"**{application['company']} — {application['role']}**")
    for entry in application.get("history", []):
        st.write(f"{entry['date']} — {entry['field']} changed to **{entry['value']}**")


@st.dialog("Edit application", width="large")
def edit_dialog(application: dict) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        company = st.text_input("Company *", value=application["company"])
        role = st.text_input("Role *", value=application["role"])
        priority = st.selectbox(
            "Priority", [p.value for p in Priority], index=[p.value for p in Priority].index(application["priority"])
        )
    with col2:
        source = st.text_input("Source", value=application.get("source", ""))
        link = st.text_input("Link", value=application.get("link", ""))
        work_mode_options = [""] + [m.value for m in WorkMode]
        work_mode = st.selectbox(
            "Work mode", work_mode_options, index=work_mode_options.index(application.get("work_mode", "") or "")
        )
    with col3:
        location = st.text_input("Location", value=application.get("location", ""))
        status = st.selectbox(
            "Status", [s.value for s in Status], index=[s.value for s in Status].index(application["status"])
        )
        stage = st.selectbox(
            "Stage", [s.value for s in Stage], index=[s.value for s in Stage].index(application["stage"])
        )
    with col4:
        resume_used = st.text_input("Resume used", value=application.get("resume_used", ""))
        desired_salary = st.text_input("Desired salary", value=application.get("desired_salary", ""))
        recruiter = st.text_input("Recruiter", value=application.get("recruiter", ""))
    with col5:
        last_contact = st.text_input("Last contact (YYYY-MM-DD)", value=application.get("last_contact") or "")
        next_step = st.text_input("Next step", value=application.get("next_step", ""))
        next_step_date = st.text_input(
            "Next step date (YYYY-MM-DD)", value=application.get("next_step_date") or ""
        )

    notes = st.text_area("Notes", value=application.get("notes", ""))

    if st.button("Save", icon=":material/check:", type="primary"):
        if not company or not role:
            st.error("Company and Role are required.")
        else:
            candidates = {
                "company": company,
                "role": role,
                "priority": priority,
                "source": source,
                "link": link,
                "work_mode": work_mode,
                "location": location,
                "status": status,
                "stage": stage,
                "resume_used": resume_used,
                "desired_salary": desired_salary,
                "recruiter": recruiter,
                "last_contact": last_contact or None,
                "next_step": next_step,
                "next_step_date": next_step_date or None,
                "notes": notes,
            }
            changes = {k: v for k, v in candidates.items() if application.get(k) != v}
            if changes:
                update_application(application["id"], changes)
            st.rerun()

    st.divider()
    confirm_delete = st.checkbox("I confirm I want to delete this application")
    if st.button("Delete application", icon=":material/delete:", disabled=not confirm_delete):
        delete_application(application["id"])
        st.session_state.selected_id = None
        st.rerun()


# --- Toolbar (reserved above the table, filled in after reading the table's selection) ---

toolbar_container = st.container()
caption_placeholder = st.empty()

# --- Table ---

applications = list_applications(filters=st.session_state.filters, sort_by=st.session_state.sort_by)

if applications:
    rows = []
    for a in applications:
        row = {key: a.get(key, "") for key, _ in COLUMNS if key != "history_summary"}
        row["history_summary"] = f"View ({len(a.get('history', []))})"
        rows.append(row)

    event = st.dataframe(
        style_table(pd.DataFrame(rows)),
        use_container_width=True,
        hide_index=True,
        column_order=[key for key, _ in COLUMNS],
        column_config={
            key: st.column_config.Column(label=label)
            for key, label in COLUMNS
        }
        | {"link": st.column_config.LinkColumn(label="Link")},
        on_select="rerun",
        selection_mode="single-row",
        key="applications_table",
    )
    st.session_state.selected_id = (
        applications[event.selection.rows[0]]["id"] if event.selection.rows else None
    )
else:
    st.session_state.selected_id = None
    st.info("No applications yet. Click Add to create one.")

# --- Fill the toolbar now that selection state is up to date for this run ---

has_selection = st.session_state.selected_id is not None

with toolbar_container:
    toolbar = st.columns([1, 1, 1, 1, 1, 6])
    if toolbar[0].button("Add", icon=":material/add:", use_container_width=True, type="primary"):
        add_dialog()
    if toolbar[1].button("Filter", icon=":material/filter_list:", use_container_width=True):
        filter_dialog()
    if toolbar[2].button("Sort", icon=":material/swap_vert:", use_container_width=True):
        sort_dialog()
    if toolbar[3].button(
        "History", icon=":material/history:", use_container_width=True, disabled=not has_selection
    ):
        selected = next((a for a in applications if a["id"] == st.session_state.selected_id), None)
        if selected:
            history_dialog(selected)
    if toolbar[4].button("Edit", icon=":material/edit:", use_container_width=True, disabled=not has_selection):
        selected = next((a for a in applications if a["id"] == st.session_state.selected_id), None)
        if selected:
            edit_dialog(selected)

active_filters = [f"{k}={v}" for k, v in st.session_state.filters.items() if v]
caption = f"Sorted by {st.session_state.sort_by}"
if active_filters:
    caption += " · filters: " + ", ".join(active_filters)
caption_placeholder.caption(caption)
