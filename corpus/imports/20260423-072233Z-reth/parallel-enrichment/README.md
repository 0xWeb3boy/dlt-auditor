# Parallel Enrichment Plan

- Repo: `/testing/reth`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260423-072233Z-reth`
- Requested worker count: `6`
- Effective worker count: `6`
- Total findings: `52`
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

- Worker 01: `9` findings, total weight `19`
- Worker 02: `8` findings, total weight `17`
- Worker 03: `8` findings, total weight `17`
- Worker 04: `9` findings, total weight `18`
- Worker 05: `9` findings, total weight `18`
- Worker 06: `9` findings, total weight `18`
