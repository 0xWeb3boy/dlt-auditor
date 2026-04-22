# Parallel Enrichment Plan

- Repo: `/testing/scroll`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260422-165556Z-scroll`
- Requested worker count: `6`
- Effective worker count: `6`
- Total findings: `14`
- Chunk strategy: `balanced_greedy_v1`

## How To Use

1. Start one worker agent per `worker-XX.md` file in this folder.
2. Give each worker its `worker-XX.md` prompt and `worker-XX-assignment.json` file.
3. Have each worker edit only the `records/`, `cards/`, and `evals/` files listed in its assignment file.
4. Review the completed edits together before merging the bundle into the long-lived corpus.

## Files

- `manifest.json`: machine-readable worker and finding assignments
- `worker-XX.md`: operator-ready prompt for that worker
- `worker-XX-assignment.json`: exact file ownership for that worker
- `worker-XX-findings.txt`: finding IDs assigned to that worker

## Worker Sizes

- Worker 01: `2` findings, total weight `5`
- Worker 02: `2` findings, total weight `5`
- Worker 03: `3` findings, total weight `6`
- Worker 04: `3` findings, total weight `6`
- Worker 05: `2` findings, total weight `4`
- Worker 06: `2` findings, total weight `4`
