# AGENTS.md

## Repo Preferences

- Always push changes to the `fork` remote.
- Do not push to `origin` unless explicitly requested.
- Do not open pull requests unless explicitly requested.
- If upstream sync is needed, merge/rebase from `origin/main` locally and then push to `fork/main`.

## Progress Tracking

- **Every time you make changes to the `materials-discovery/` directory, you MUST update
  `materials-discovery/Progress.md`.**
  - Add a row to the **Changelog** table (date, change title, details).
  - Append a timestamped entry to the **Diary** section under today's date heading.
  - This applies to ALL changes: code, configs, experiments, fixes, refactors, docs, new systems, etc.
