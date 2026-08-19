# Orome Hunter Constitution

Principles that govern every product and technical decision in this project. Any spec or plan that contradicts them must justify it explicitly or be adjusted.

## 1. Personal tool, not a product
Built for a single user (the repo owner). No auth, multi-tenancy, roles, or i18n unless a future spec explicitly asks for it. This simplifies every downstream decision: no login, no permissions, no data isolation between users.

## 2. Tech-free specs, tech-full plans
`spec.md` files describe WHAT and WHY, in business/user language. They never mention frameworks, languages, or databases. Those decisions live in `plan.md`, one per spec, and can be reconsidered without touching the spec.

## 3. Small, usable increments
Each numbered spec (001, 002, ...) delivers something usable on its own. We don't spec "the whole system" at once. The application tracker (001) is the foundation; the job-offer aggregator and analytics come after and build on the data it generates.

## 4. Simplicity over speculative scale
Single user, low data volume (tens/hundreds of applications, not millions). We do not design for scale, concurrency, or high availability. Prefer SQLite/a local file over server infrastructure, unless a concrete spec's plan justifies otherwise.

## 5. Verifiable acceptance criteria
Every user story in a spec must have concrete acceptance criteria (given/when/then or equivalent), so implementation tasks can be derived and "done" is unambiguous.

## 6. Documentation language
All `.md` files in this repo (constitution, specs, plans, tasks) are written in English, regardless of the language used in conversation while building them.

## 7. Ask before running tests
Never run the test suite, or any part of it, without asking first. Always confirm whether the user wants tests run at that point before executing `pytest` or similar.

## 8. Mark features as testable or not
When a feature or task is finished, mark it as "testable" or "not testable" before writing automated tests for it. Only write tests for what's marked testable, so effort doesn't go into testing things that don't add value.

## 9. Avoid emojis
Always avoid emojis, in any chat response or HTML component.

## 10. Current status
- 001 Application tracker — implemented (model, storage, UI, unit tests passing); pending the user's manual smoke test (tasks.md T015).
- 002 Job-offer search/aggregator — pending, depends on 001.
- 003 Personal analytics — pending, depends on 001.
