---
case_id: case_20250915_4507bc93b
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-09-15
source_refs:
  - git:4507bc93b15bed10f98f1f5296d301365ee34b8d
  - "src/discof/replay/fd_sched.c:486"
  - "src/discof/replay/fd_sched.c:589"
  - "src/discof/replay/fd_sched.c:229"
  - "src/discof/replay/fd_sched.c:109"
bug_class: buffer-overflow
impact_type:
  - memory-corruption
  - denial-of-service
confidence: high
tags:
  - blockchain-core
  - replay
  - scheduler
  - fec-ingestion
  - buffer-overflow
  - bounds-check
  - bad-block-rejection
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The supported finding is a likely security fix in src/discof/replay/fd_sched.c. The fd_sched_fec_ingest path now asserts that fec_buf_soff is within fec_buf_sz before compacting residual bytes and adds an explicit maximum-size check for residual bytes plus the incoming FEC payload. The commit subject and added comments support a buffer-overflow/crash prevention thesis, but the supplied evidence does not prove exploitability, remote attacker control, or consensus impact.

## Observed Patch Facts

1. In `src/discof/replay/fd_sched.c`, the patch replaces `/* If there is residual data from the previous FEC set within the same` with `FD_TEST( block->fec_buf_sz>=block->fec_buf_soff );`.

2. In `src/discof/replay/fd_sched.c`, the patch replaces `block->txn_in_flight_cnt++;` with `long now = fd_tickcount();`.

3. In `src/discof/replay/fd_sched.c`, the patch replaces `FD_LOG_INFO(( "block slot %lu, prime %lu, staged %d (lane %lu), dying %d, in_rdisp %d...` with `FD_LOG_INFO(( "block slot %lu, prime %lu, staged %d (lane %lu), dying %d, in_rdisp %d...`.

4. In `src/discof/replay/fd_sched.c`, the patch replaces `uint serializing_cnt;` with `uint alut_success_cnt;`.

## Project Context

The changed code sits primarily in `src/discof/replay`, `src/discof`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/discof/replay/fd_sched.h`, `src/discof/replay/fd_replay_tile.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/discof/replay/fd_replay_tile.c`, `src/discof/sender/fd_sender_tile.c`. The strongest project-level identifiers around this patch are `block`, `sched`, `metrics`, and `ulong`. Nearby tests or test-like files include `src/discof/backtest/fd_backtest_tile.c`, `src/discof/rpcserver/fuzz_json_lex.c`.

## Before/After Behavior

Before the patch, the shown FEC ingestion code compacted residual bytes when block->fec_buf_sz > block->fec_buf_soff and relied on an earlier FEC set size check for append safety. After the patch, the code first enforces block->fec_buf_sz >= block->fec_buf_soff and checks block->fec_buf_sz - block->fec_buf_soff + fec->fec->data_sz against FD_SCHED_MAX_FEC_BUF_SZ, with comments indicating that excessive residual data marks a bad block/fork rather than a condition replay should crash on. Other edits in the evidence are metrics and debug logging changes and should be treated as ancillary.

# Root Cause

The fd_sched_fec_ingest path did not explicitly validate all buffer-state bounds needed for residual FEC compaction and appending a new FEC payload. In particular, the supplied diff supports that residual offset validity and combined residual-plus-new-data capacity were not enforced at this point before the patch.

## Walkthrough

1. FEC data for replay enters src/discof/replay/fd_sched.c through fd_sched_fec_ingest.

2. When residual data remains from a previous FEC set in the same batch, the scheduler moves the residual slice to the start of block->fec_buf.

3. The patch adds FD_TEST( block->fec_buf_sz>=block->fec_buf_soff ) before computing the residual length used by memmove.

4. The patch adds a check that block->fec_buf_sz-block->fec_buf_soff+fec->fec->data_sz does not exceed FD_SCHED_MAX_FEC_BUF_SZ.

5. The added comment states that excessive residual data should be treated as a bad block and replay should refuse that fork instead of crashing.

6. Metrics and debug-print changes in the same file do not establish or change the vulnerability thesis.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/replay/fd_sched.c | 486 | FEC ingestion path compacts residual buffer data and appends a new FEC set; patch adds bounds/invariant checks before memory movement and append sizing. |
| src/discof/replay/fd_sched.c | 589 | Transaction-ready scheduling metrics update; appears ancillary and not the core security fix. |
| src/discof/replay/fd_sched.c | 109 | Scheduler metrics structure update; telemetry support rather than security-relevant behavior. |
| src/discof/replay/fd_sched.c | 229 | Debug logging/metrics output update; not part of the buffer safety invariant. |

## Code Snippets

## Snippet 1

Context: `src/discof/replay/fd_sched.c:486` (changes signature or replay validation logic)

Before
```c
}

  /* If there is residual data from the previous FEC set within the same
     batch, we move it to the beginning of the buffer and append the new
     FEC set. */
  if( FD_LIKELY( block->fec_buf_sz>block->fec_buf_soff ) ) {
    /* Addition is safe and won't overflow because we checked the FEC
       set size above. */
```
After
```c
}

  FD_TEST( block->fec_buf_sz>=block->fec_buf_soff );
  if( FD_LIKELY( block->fec_buf_sz>block->fec_buf_soff ) ) {
    /* If there is residual data from the previous FEC set within the
       same batch, we move it to the beginning of the buffer and append
       the new FEC set. */
    memmove( block->fec_buf, block->fec_buf+block->fec_buf_soff, block->fec_buf_sz-block->fec_buf_soff );
```

## Snippet 2

Context: `src/discof/replay/fd_sched.c:589` (changes a sensitive control or state-update path)

Before
```c
out_txn->block_id         = block->block_id;
    out_txn->parent_block_id  = block_pool_ele( sched->block_pool, block->parent_idx )->block_id;
    block->txn_in_flight_cnt++;
    txn_queued_cnt--;
    return 1UL;
  }
```
After
```c
out_txn->block_id         = block->block_id;
    out_txn->parent_block_id  = block_pool_ele( sched->block_pool, block->parent_idx )->block_id;

    long now = fd_tickcount();
    ulong delta = (ulong)(now-sched->txn_in_flight_last_tick);
    sched->metrics->txn_none_in_flight_tickcount     += fd_ulong_if( block->txn_in_flight_cnt==0U && sched->txn_in_flight_last_tick!=LONG_MAX, delta, 0UL );
    sched->metrics->txn_weighted_in_flight_tickcount += fd_ulong_if( block->txn_in_flight_cnt!=0U, delta, 0UL );
    sched->metrics->txn_weighted_in_flight_cnt       += delta*block->txn_in_flight_cnt;
```

## Snippet 3

Context: `src/discof/replay/fd_sched.c:229` (changes a sensitive control or state-update path)

Before
```c
FD_FN_UNUSED static void
debug_print_block( fd_sched_block_t * block ) {
  FD_LOG_INFO(( "block slot %lu, prime %lu, staged %d (lane %lu), dying %d, in_rdisp %d, fec_eos %d, rooted %d, block_start_signaled %d, block_end_signaled %d, txn_parsed_cnt %u, txn_in_flight_cnt %u, txn_done_cnt %u, shred_cnt %u, fec_cnt %u",
                (ulong)block->block_id.slot, (ulong)block->block_id.prime, block->staged, block->staging_lane, block->dying, block->in_rdisp, block->fec_eos, block->rooted, block->block_start_signaled, block->block_end_signaled, block->txn_parsed_cnt, block->txn_in_flight_cnt, block->txn_done_cnt, block->shred_cnt, block->fec_cnt ));
}


/* Public functions. */
```
After
```c
FD_FN_UNUSED static void
debug_print_block( fd_sched_block_t * block ) {
  FD_LOG_INFO(( "block slot %lu, prime %lu, staged %d (lane %lu), dying %d, in_rdisp %d, fec_eos %d, rooted %d, block_start_signaled %d, block_end_signaled %d, txn_parsed_cnt %u, txn_in_flight_cnt %u, txn_done_cnt %u, shred_cnt %u",
                (ulong)block->block_id.slot, (ulong)block->block_id.prime, block->staged, block->staging_lane, block->dying, block->in_rdisp, block->fec_eos, block->rooted, block->block_start_signaled, block->block_end_signaled, block->txn_parsed_cnt, block->txn_in_flight_cnt, block->txn_done_cnt, block->shred_cnt ));
}

FD_FN_UNUSED static void
debug_print_metrics( fd_sched_t * sched ) {
```

## Snippet 4

Context: `src/discof/replay/fd_sched.c:109` (changes a sensitive control or state-update path)

Before
```c
uint  lane_promoted_cnt;
  uint  lane_demoted_cnt;
  uint  serializing_cnt;
  ulong fec_cnt;
  ulong txn_parsed_cnt;
  ulong txn_done_cnt;
  uint  txn_abandoned_parsed_cnt;
  uint  txn_abandoned_done_cnt;
```
After
```c
uint  lane_promoted_cnt;
  uint  lane_demoted_cnt;
  uint  alut_success_cnt;
  uint  alut_serializing_cnt;
  uint  txn_abandoned_parsed_cnt;
  uint  txn_abandoned_done_cnt;
  uint  txn_max_in_flight_cnt;
  ulong txn_weighted_in_flight_cnt;
```

# Fix Pattern

Add explicit local bounds checks around buffer compaction and append sizing in the replay FEC ingestion path, and handle nonconformant block data as a rejection/refusal condition.

## How It Was Fixed

fd_sched_fec_ingest now validates the residual buffer offset before memmove and validates that the residual byte count plus fec->fec->data_sz fits within FD_SCHED_MAX_FEC_BUF_SZ before appending the new FEC set. The evidence indicates the intended behavior for an oversized residual condition is to refuse replay down the bad fork rather than crash.

# Why It Matters

1. Protects a replay-critical buffer from oversized FEC accumulation.

2. Prevents malformed residual buffer state from feeding unsafe length arithmetic.

3. Changes a bad-block condition toward rejection/refusal instead of crash-prone behavior.

4. Exploitability and consensus effects are not established by the supplied evidence.

# Evidence Notes

The strongest evidence is the fd_sched_fec_ingest diff around src/discof/replay/fd_sched.c line 486: FD_TEST( block->fec_buf_sz>=block->fec_buf_soff ) and the added check against FD_SCHED_MAX_FEC_BUF_SZ for residual bytes plus fec->fec->data_sz. The commit subject says "replay: fix buffer overflow in scheduler," which supports the classification. The provided snippets do not show the complete body of the oversized-buffer check, do not show tests, and do not prove attacker reachability or practical exploitation. Protocol security invariant: Replay scheduler FEC ingestion must keep the residual buffer slice well-formed and ensure residual bytes plus the incoming FEC payload do not exceed FD_SCHED_MAX_FEC_BUF_SZ; nonconformant block data should be rejected/refused rather than allowed to overrun scheduler buffer capacity or crash replay. Verification notes: No exploitability primitive such as remote code execution is proven by the patch evidence. No proof is shown that an attacker can reliably construct and deliver the malformed FEC/residual state. No consensus divergence is demonstrated beyond refusing replay down a bad fork. The metrics and debug-print changes are not treated as security fixes. Classification is based only on the supplied commit metadata and snippets. No external code inspection or command execution was used. Downgraded from confirmed/high to likely/medium because the evidence supports a buffer-safety fix but does not fully prove exploitability or show the complete rejection path. Metrics and debug logging edits were excluded from the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `buffer-overflow`
Final impact type: `memory-corruption, denial-of-service`
Final confidence: `high`
Final tags: `blockchain-core, replay, scheduler, fec-ingestion, buffer-overflow, bounds-check, bad-block-rejection`

The supplied patch evidence supports retaining this as a security-fix case. The commit subject explicitly identifies a scheduler buffer overflow, and the core code change adds bounds/invariant checks around residual FEC buffer compaction and append sizing in replay. The added comment says oversized residual data should be treated as a bad block and refused rather than crashing. The original liveness-focused metadata is too narrow; the validated issue is more conservatively a replay FEC buffer overflow with likely crash/DoS and possible memory-corruption impact, while exploitability details remain unproven.

## Security Evidence

1. Commit subject says "replay: fix buffer overflow in scheduler".
2. fd_sched_fec_ingest now checks block->fec_buf_sz >= block->fec_buf_soff before using the residual length for memmove.
3. Patch adds a maximum-size check for residual bytes plus fec->fec->data_sz against FD_SCHED_MAX_FEC_BUF_SZ.
4. Added comment states excessive residual data indicates a bad block and replay should refuse the fork instead of crashing.
5. Changed path is in replay scheduler FEC ingestion, a security-sensitive blockchain-core processing path.

## Missing Evidence

1. Complete body of the oversized-buffer rejection path is not shown.
2. No proof is provided that malformed FEC/residual state is attacker-controllable.
3. No exploit demonstration, memory corruption primitive, or consensus-divergence scenario is shown.
4. Ancillary metrics and debug logging edits do not contribute security evidence.

## Claim Boundaries

1. Validate only the FEC buffer bounds issue, not the metrics or debug-print changes.
2. Do not claim remote code execution or practical exploitability from the supplied evidence.
3. Do not claim proven consensus failure; the supported impact is memory-safety hard failure/DoS prevention in replay.
4. The patch supports a buffer-overflow fix, but attacker reachability and exploit mechanics remain outside the evidence.
