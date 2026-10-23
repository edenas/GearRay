# Archived execution records

Completed raw JSONL journals, the original executed removal manifest and the prior catalog snapshot retain their exact bytes in execution-journals.zip. The current final keeper/removal manifest stays directly accessible. Use execution-journal-catalog.json for the earlier raw records; they are archive-resolvable, not live loose files.

```powershell
py -3.12 tools/maintenance/restore_history.py --catalog docs/maintenance/2026-10-23/implementation/execution-journal-catalog.json --list
py -3.12 tools/maintenance/restore_history.py --catalog docs/maintenance/2026-10-23/implementation/execution-journal-catalog.json --entry docs/maintenance/2026-10-23/implementation/executed-removal-manifest.json --dest build/history-restore/execution-journal
```

Earlier journal headers identify the exact original manifest hash. runtime-retention-reclassification.json explains the seven runtime objects moved to local-only retention and how the original generated keeper ZIP is preserved locally. The final catalog/manifest records current keepers. Original historical payloads and the 27 pre-existing archives are unchanged.
