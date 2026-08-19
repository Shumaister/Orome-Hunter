# Spec 001: Application Tracker

**Status:** Draft, plan defined
**Depends on:** nothing (this is the foundation)

## Summary

As a job seeker, I need a single place to record every application I make, with all its relevant data, see what stage it's in, and update it as it progresses (or falls through), so I don't lose track of my search and can make decisions (who to follow up with, how many active applications I have, etc.).

This is the base increment of the project. The data it generates (applications, stages, dates) is the input that the future job-offer aggregator (002) and analytics (003) specs will use.

## Data model: Application

| Field | Values / type | Required | Notes |
|---|---|---|---|
| Priority | High / Medium / Low | No (default: Medium) | Set by the user, not calculated |
| Company | Text | Yes | |
| Role / Position | Text | Yes | |
| Source | Text (e.g. LinkedIn, referral, company website) | No | |
| Link | URL | No | Link to the original job posting |
| Work mode | Hybrid / Remote | No | |
| Location | Text | No | City/country if applicable (relevant for hybrid) |
| Application date | Date | Yes | Default: today |
| Resume used | Text | No | Name/version of the resume sent, e.g. "Resume_Backend_v3" |
| Desired salary | Text/number | No | |
| Status | On hold / Active / Offer / Rejected / Closed / Withdrawn | Yes | Default: Active. Coarse category of the process |
| Stage | Application / Recruiter / HR Interview / Technical Interview / Client Interview / Final Interview / Offer / Closed | Yes | Default: Application. Specific step within the pipeline, independent of Status |
| Recruiter | Text | No | Name/contact of the HR person |
| Last contact | Date | No | |
| Next step | Text | No | What's coming up / being waited on |
| Next step date | Date | No | |
| Days since application | Calculated | — | `today - Application date`, not entered manually, recalculated on display |
| Feedback / Notes | Free text | No | No reasonable length limit |

**Note:** "Status" and "Stage" are independent. Status answers "how is this going overall?" (for quickly filtering active vs. closed). Stage answers "what specific step of the process am I at?" (to know what's next). Both can be updated at any time, in any order, because in real life steps get skipped or things go backward.

## User stories

### H1 — Register an application
As a user, I want to register a new application with all its data (see table above) so I don't rely on memory or a loose spreadsheet.

**Acceptance criteria:**
- Given I want to register an application, when I enter at least Company and Role, then the application is saved with Application date = today, Status = Active, and Stage = Application by default.
- I can fill in the rest of the optional fields at creation time or later.

### H2 — View all my applications
As a user, I want to see all my applications at a glance, to understand the overall state of my search.

**Acceptance criteria:**
- I can see a list/board with all applications, showing at least: Company, Role, Priority, Status, Stage, Days since application.
- Days since application is calculated and always shown up to date (not a stored value that goes stale).
- I can filter by Status, by Stage, and by Priority.
- I can sort by Application date (default: most recent first) and by Days since application.

### H3 — Update Stage and Status of an application
As a user, I want to move an application through stages and adjust its status as the process progresses, to reflect reality and know what needs my attention.

**Acceptance criteria:**
- I can change the Stage of an application to any of the defined values, at any time.
- I can change the Status of an application to any of the defined values, at any time, independently of Stage.
- Every change of Stage and of Status is recorded with a date, so the timeline of that application can later be reconstructed (this enables analytics in spec 003).

### H4 — Edit and delete an application
As a user, I want to fix data I entered incorrectly or remove a duplicate/mistaken application.

**Acceptance criteria:**
- I can edit any field of an existing application.
- I can delete an application. Deleting it also removes its Stage/Status history (simple delete, no trash bin in v1).

### H5 — Follow-up and notes
As a user, I want to note feedback, who the recruiter is, when the last contact was, and what the next step is, so I don't forget anything during the process.

**Acceptance criteria:**
- I can enter/edit Recruiter, Last contact, Next step, Next step date, and Feedback/Notes at any time, on any application.

## Out of scope (v1)

- Authentication / multi-user (see constitution, principle 1).
- Automatic reminders/notifications (Next step and its date are stored as data, but don't trigger alerts in v1).
- Automatic import of applications from email or LinkedIn.
- Attaching files (resume, cover letter) to an application — only the resume's name/reference is stored, not the file itself.
- Analytics/metrics (that's spec 003).
- Job-offer search/aggregation (that's spec 002).

## Open questions

None pending. Decision made: runs locally, on a single machine (see `plan.md` for technical detail).
