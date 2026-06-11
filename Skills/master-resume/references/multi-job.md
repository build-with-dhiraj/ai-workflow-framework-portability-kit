# Multi-Job Batch Mode

For 3–5 similar jobs at once. The win: **one shared discovery session** addressing gaps deduplicated across all jobs (typically 11–27% time saving vs one-at-a-time). Trigger when the user provides multiple JDs or asks to apply to several roles.

## Pipeline
```
Intake & batch init → Aggregate gap analysis (dedup) → Shared discovery (single session)
→ Per-job processing → Batch finalization
```

1. **Intake & batch init.** Collect all JDs. Create `output/batches/batch-<date>-<slug>/` and `_batch_state.json`. One job record per JD (schema below).
2. **Aggregate gap analysis.** Run research + matching per job to get each job's gaps, then **deduplicate** across jobs. Write `_aggregate_gaps.md` ranking by leverage: HIGH (3+ jobs) / MEDIUM (2) / LOW (1). Fewer unique gaps than total gaps = the saving.
3. **Shared discovery.** Run [discovery.md](discovery.md) ONCE across the deduped gaps, leading each with its leverage line. Write `_discovered_experiences.md`, tag each with the job IDs it serves, and push approved items to the library.
4. **Per-job processing.** Process job 1 in **interactive** mode (checkpoints at research, template, matching). Offer to switch to **express** mode for jobs 2…N (auto-proceed, generate, no checkpoints). Each job still gets its own lens, bullet plan, generation, fingerprint scan, and critique.
5. **Batch finalization.** Write `_batch_summary.md`: every job with coverage %, score, files, and any remaining gaps. Offer to push all approved resumes' new bullets back to the library.

## Job schema (`_batch_state.json` → jobs[])
```json
{
  "job_id": "job-1",
  "company": "Microsoft",
  "role": "Principal PM",
  "jd_text": "...",
  "jd_url": "https://...",
  "priority": "high",
  "status": "pending|in_progress|completed|failed",
  "current_phase": "research|template|matching|generation|null",
  "requirements": ["..."],
  "gaps": [],
  "coverage": 85,
  "files_generated": true
}
```
Lifecycle: `pending → in_progress → completed` (or `failed`). Phase order within `in_progress`: research → template → matching → generation.

## Resumability
`_batch_state.json` is the source of truth. On re-entry, read it and continue from each job's `status`/`current_phase` — never restart completed jobs. If interrupted mid-discovery, the partial `_discovered_experiences.md` plus the library updates already made are safe to resume from.

## Mode guidance
- **Interactive** for the first job and any job where the role differs meaningfully — the user calibrates framing once.
- **Express** for the remaining similar jobs once the user trusts the framing. Always still run the fingerprint scan and verification gate; only the human checkpoints are skipped.
