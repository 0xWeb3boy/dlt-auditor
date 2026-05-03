---
case_id: case_20260109_1ad8a534f
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2026-01-09
source_refs:
  - git:1ad8a534fb2ad5bdbf67ed701695f17022e1f2f9
  - "src/discof/forest/fd_forest.c:693"
  - "src/discof/forest/fd_forest.h:17"
  - "src/discof/repair/fd_repair_tile.c:731"
  - "src/discof/forest/fd_forest.c:836"
bug_class: merkle-root-validation-hardening
impact_type:
  - consensus-integrity
  - data-integrity
confidence: medium
tags:
  - blockchain-core
  - validator
  - repair
  - fec
  - merkle-root
  - equivocation-protection
  - consensus-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix for repair/forest FEC merkle validation. It adds explicit merkle-root tracking, rejects incoming data shreds that conflict with an already verified confirmed merkle root, verifies chained FEC roots from a confirmed root, and resumes verification after completion of a previously incorrect FEC. The evidence supports validation of equivocated or conflicting repaired shred state, but does not prove a concrete exploit path or finalized-consensus failure.

## Observed Patch Facts

1. In `src/discof/forest/fd_forest.c`, the patch replaces `fd_forest_blk_idxs_insert_if( ele->fecs, fec_set_idx > 0, fec_set_idx - 1 );` with `/* Pre-filtering on merkle root.`.

2. In `src/discof/forest/fd_forest.h`, the patch replaces `/* FD_FOREST_USE_HANDHOLDING: Define this to non-zero at compile time` with `/* Merkle root tracking.`.

3. In `src/discof/repair/fd_repair_tile.c`, the patch replaces `if( FD_UNLIKELY( ctx->profiler.enabled ) ) {` with `/* If we just completed something that underwent verification surgery,`.

4. In `src/discof/forest/fd_forest.c`, the patch replaces `void` with `fd_forest_blk_t *`.

## Project Context

The changed code sits primarily in `src/discof/forest`, `src/discof`, `src/discof/repair`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/discof/forest/test_forest.c`, `src/discof/repair/fd_policy.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/discof/forest/test_forest.c`, `src/discof/replay/fd_replay_tile.c`. The strongest project-level identifiers around this patch are `merkle`, `root`, `slot`, and `fec_set_idx`. Nearby tests or test-like files include `src/discof/backtest/test_backtest_shredcap.c`, `src/discof/backtest/shredcap.md`.

## Before/After Behavior

Before the shown change, `fd_forest_data_shred_insert` updated FEC/shred index bookkeeping without evidence of a merkle-root prefilter in that location. After the change, it computes the FEC index, checks whether the confirmed merkle root for that FEC boundary has been verified, compares the incoming root against the stored confirmed root, and returns `NULL` on mismatch. The patch also adds documented per-FEC merkle-root tracking, introduces chained FEC verification from a confirmed root, and re-triggers confirmation processing when a previously incorrect repaired FEC completes.

# Root Cause

The supplied evidence indicates the repair forest did not have the shown enforcement tying later repaired data shreds and completed FEC state back to a verified confirmed merkle-root chain. This could allow conflicting FEC merkle-root state to remain in repair/forest processing until the new rejection and chained-verification logic was added.

## Walkthrough

1. Repair forest state tracks slots, shreds, and FEC sets used by repair and replay-adjacent processing.

2. The patch documents a model where each FEC set records a merkle root and later shreds for the same FEC are compared against it.

3. When a confirmed merkle root for a FEC boundary is already verified, `fd_forest_data_shred_insert` now compares incoming shred state against that root.

4. If the incoming merkle root differs from the verified confirmed root, insertion returns `NULL` and the conflicting shred is not accepted through that path.

5. The new `fd_forest_fec_chain_verify` records the confirmed root, marks the FEC boundary verified, and walks chained FEC state until confirmation or mismatch.

6. If the expected merkle root does not match recorded FEC state, verification stops at the mismatching block instead of treating the chain as valid.

7. After a previously incorrect FEC completes, the repair tile re-runs confirmation continuation so repaired state can be checked again.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/forest/fd_forest.c | 693 | Data shred insertion now pre-filters against verified confirmed merkle roots and rejects conflicting shreds. |
| src/discof/forest/fd_forest.h | 17 | Defines the repair forest merkle-root tracking model for FEC sets and duplicate/conflicting roots. |
| src/discof/forest/fd_forest.c | 836 | Adds chained FEC verification from a confirmed block/root and stops on merkle mismatch. |
| src/discof/repair/fd_repair_tile.c | 731 | After repaired FEC completion, resumes chained merkle verification for previously incorrect or incomplete FEC state. |

## Code Snippets

## Snippet 1

Context: `src/discof/forest/fd_forest.c:693` (changes persisted or aggregate state handling)

Before
```c
if( FD_UNLIKELY( !ele ) ) FD_LOG_ERR(( "fd_forest: fd_forest_data_shred_insert: ele %lu is not in the forest. data_shred_insert should be preceded by blk_insert", slot ));
# endif
  fd_forest_blk_idxs_insert_if( ele->fecs, fec_set_idx > 0, fec_set_idx - 1 );
  fd_forest_blk_idxs_insert_if( ele->fecs, slot_complete,   shred_idx       );
```
After
```c
if( FD_UNLIKELY( !ele ) ) FD_LOG_ERR(( "fd_forest: fd_forest_data_shred_insert: ele %lu is not in the forest. data_shred_insert should be preceded by blk_insert", slot ));
# endif

  /* Pre-filtering on merkle root.
     If we have knowledge of the confirmed merkle root, we can reject
     shreds that don't match it.  Else, we'll accept any and all shreds,
     and invalidating the merkle root if we see more than 1 version of
     the FEC. */
```

## Snippet 2

Context: `src/discof/forest/fd_forest.h:17` (changes signature or replay validation logic)

Before
```c
tree forwards (using BFS). */

/* FD_FOREST_USE_HANDHOLDING:  Define this to non-zero at compile time
   to turn on additional runtime checks and logging. */
```
After
```c
tree forwards (using BFS). */

/* Merkle root tracking.
   For each FEC set in the slot, we record the merkle root of the first
   shred we receive in `.merkle_roots[ fec_set_idx / 32 ]`. Then for any
   shred in the same FEC inserted later, the merkle root of the new
   shred is compared to the merkle root we have stored.
```

## Snippet 3

Context: `src/discof/repair/fd_repair_tile.c:731` (changes persisted or aggregate state handling)

Before
```c
}

  if( FD_UNLIKELY( ctx->profiler.enabled ) ) {
    // If turbine slot 0 is in the consumed frontier, and it satisfies the
```
After
```c
}

  /* If we just completed something that underwent verification surgery,
     re-trigger continuation of chained merkle verification. */
  if( FD_UNLIKELY( ctx->last_incorrect_fec->slot == ele->slot && ctx->last_incorrect_fec->fec_set_idx == shred->fec_set_idx ) ) {
    fd_forest_blk_t * ele = fd_forest_query( ctx->forest, ctx->last_incorrect_fec->slot );
    FD_TEST( fd_forest_merkle_test( ele->merkle_verified, (ele->complete_idx / 32UL) + 1 ) ); /* we should have verified this FEC block id at least */
    after_confirmed( ctx, ele->slot, &ele->merkle_roots[ (ele->complete_idx / 32UL) + 1 ].cmr );
```

## Snippet 4

Context: `src/discof/forest/fd_forest.c:836` (changes a sensitive control or state-update path)

Before
```c
}

void
fd_forest_fec_clear( fd_forest_t * forest, ulong slot, uint fec_set_idx, uint max_shred_idx ) {
```
After
```c
}

fd_forest_blk_t *
fd_forest_fec_chain_verify( fd_forest_t * forest, fd_forest_blk_t * ele, fd_hash_t const * bid ) {
  FD_TEST( ele && ele->complete_idx != UINT_MAX && ele->consumed );

  fd_hash_t const * expected_mr = bid;
  uint fec_idx = ele->complete_idx / 32UL;
```

# Fix Pattern

Add explicit confirmed merkle-root state for FEC boundaries, reject incoming shreds that conflict with verified roots, and resume chained verification when repaired FEC completion changes previously incorrect state.

## How It Was Fixed

The patch adds merkle-root tracking semantics in the forest, adds a prefilter in data shred insertion for verified confirmed-root mismatches, introduces chained FEC merkle verification, and updates repair completion handling to continue verification after an incorrect FEC is repaired.

# Why It Matters

1. Rejects shreds that conflict with an already verified confirmed merkle root.

2. Makes FEC equivocation or duplicate conflicting roots detectable in repair forest state.

3. Improves validation before repaired shred state can continue through repair/replay-adjacent processing.

4. The evidence does not establish a concrete remote exploit or finalized-consensus impact.

# Evidence Notes

Grounded evidence comes from `src/discof/forest/fd_forest.c` in `fd_forest_data_shred_insert`, which now rejects mismatched roots when a confirmed merkle root has been verified; `src/discof/forest/fd_forest.h`, which documents per-FEC merkle-root tracking and conflict handling; `fd_forest_fec_chain_verify`, which records confirmed roots and stops on mismatch; and `src/discof/repair/fd_repair_tile.c`, which resumes verification after completion of a previously incorrect FEC. Claims about signature forgery, cryptographic primitive failure, remote exploitability, or proven invalid finalization are not supported by the supplied evidence. Protocol security invariant: Repair forest state should not accept or continue confirming repaired shreds whose FEC merkle roots conflict with a verified confirmed merkle root for the relevant FEC boundary. Verification notes: No concrete remote exploit sequence is proven by the provided patch evidence. No direct signature forgery or cryptographic primitive break is shown. No proof is provided that invalid shreds reached finalized consensus before the patch. The exact impact of duplicate confirmation repair on fork choice or replay output is not fully shown. The classification relies on repair/forest merkle validation behavior, not on unrelated GUI, command, or shredcap file touches. Supported as likely security-relevant because the patch enforces a consensus/replay-adjacent merkle validation invariant. Confidence is medium because the evidence shows validation hardening but not an end-to-end exploit or impact demonstration. No helper file is treated as the root cause. Unrelated touched files are not used to broaden the claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `merkle-root-validation-hardening`
Final impact type: `consensus-integrity, data-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, validator, repair, fec, merkle-root, equivocation-protection, consensus-validation`

The supplied evidence supports keeping this as security hardening, not a proven security fix. The patch tightens validator repair/forest handling by tracking FEC merkle roots, rejecting shreds that conflict with an already verified confirmed merkle root, and continuing chained verification after repaired FEC completion. That is security-sensitive consensus/data-integrity hardening, but the patch evidence does not prove an end-to-end exploit, request forgery, signature validation failure, or finalized consensus break.

## Security Evidence

1. Commit subject explicitly references FEC chaining verification, duplicate confirmation repair, and equivocation protection.
2. Data shred insertion now rejects an incoming shred when its merkle root conflicts with a verified confirmed merkle root.
3. New merkle-root tracking documents detection of conflicting roots within the same FEC set.
4. New chained FEC verification records confirmed roots and stops when expected merkle roots do not match.
5. Repair tile resumes verification after completion of a previously incorrect FEC.

## Missing Evidence

1. No concrete attacker flow or exploit sequence is shown.
2. No evidence of signature forgery or cryptographic primitive failure is provided.
3. No proof that conflicting shreds previously reached finalized consensus or caused validator compromise is shown.
4. No full before/after test demonstrating an externally exploitable security failure is included.

## Claim Boundaries

1. Classify as validation hardening around repair/forest FEC merkle roots, not as request forgery or signature validation.
2. Do not claim a proven remote exploit from the supplied patch alone.
3. Do not claim finalized-consensus failure; the evidence supports rejection of conflicting repaired shred state.
4. Security relevance is limited to consensus-adjacent data integrity and equivocation protection in repair handling.
