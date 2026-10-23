# Archived raw evidence

The following original payloads are retained byte-for-byte in the versioned history catalog. Historical links to them require restoration; they are not live loose-file links. Reports, scripts and small summaries remain accessible.

- `frame-samples.csv`
- `scenario-fixtures.json`
- `stage-samples.csv`

From the repository root, list entries or restore an exact original path under a safe case directory:

```powershell
py -3.12 tools/maintenance/restore_history.py --list --entry docs/performance/2026-10-19/post-implementation-review/evidence/canonical-replay
py -3.12 tools/maintenance/restore_history.py --entry docs/performance/2026-10-19/post-implementation-review/evidence/canonical-replay/frame-samples.csv --dest build/history-restore/raw-evidence
```

Catalog: `docs/history/2026-10-23/catalog.json`. See `docs/HISTORY.md` for archive policy and historical-link classification.
