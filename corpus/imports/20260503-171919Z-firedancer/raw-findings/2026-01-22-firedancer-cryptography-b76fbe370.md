---
case_id: case_20260122_b76fbe370
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2026-01-22
source_refs:
  - git:b76fbe370bfdc856ffb5f420f3630d7db9fa2ae8
  - "src/discof/restore/utils/fd_ssload.c:112"
  - "src/discof/replay/fd_sched.c:1061"
  - "src/discof/replay/fd_sched.c:1762"
  - "src/discof/replay/fd_sched.c:1692"
bug_class: consensus-poh-validation
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - blockchain-core
  - validator
  - consensus
  - replay
  - poh
  - tick-verification
  - snapshot
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix in Firedancer's replay scheduler. The grounded change is that block completion now calls verify_ticks(block) before emitting a normal block-end task, and a failed check marks the bank/block dead. The snapshot loader also changes absent hashes_per_tick handling from DEFAULT_HASHES_PER_TICK to 0UL, explicitly tying that value to hash verification semantics. The evidence supports a replay/consensus validation issue, but not a concrete exploit path or proof of finalized invalid state.

## Observed Patch Facts

1. In `src/discof/restore/utils/fd_ssload.c`, the patch replaces `else fd_bank_hashes_per_tick_set( bank, DEFAULT_HASHES_PER_TICK );` with `/* https://github.com/anza-xyz/agave/blob/v3.0.6/ledger/src/blockstore_processor.rs#L...`.

2. In `src/discof/replay/fd_sched.c`, the patch replaces `out->task_type = FD_SCHED_TT_BLOCK_END;` with `if( FD_UNLIKELY( verify_ticks( block ) ) ) {`.

3. In `src/discof/replay/fd_sched.c`, the patch removes `/* FIXME what happens if someone sends us mblks_rem==0UL here? */`.

4. In `src/discof/replay/fd_sched.c`, the patch replaces `CHECK_LEFT( sizeof(fd_microblock_hdr_t) );` with `if( FD_UNLIKELY( block->mblk_cnt>=FD_SCHED_MAX_MBLK_PER_SLOT ) ) {`.

## Project Context

The changed code sits primarily in `src/discof/restore/utils`, `src/discof/restore`, `src/discof/replay`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/discof/restore/utils/fd_ssmanifest_parser.c`, `src/discof/restore/utils/fd_ssmsg.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/discof/restore/utils/fd_ssmsg.h`, `src/discof/restore/utils/fd_ssmanifest_parser.c`. The strongest project-level identifiers around this patch are `block`, `mblk_cnt`, `bank`, and `hash`. Nearby tests or test-like files include `src/discof/restore/utils/fuzz_ssmanifest_parser.c`, `src/discof/restore/utils/fuzz_sshttp.c`.

## Before/After Behavior

Before the patch, the provided fd_sched_task_next_ready() evidence shows block_should_signal_end(block) leading directly to FD_SCHED_TT_BLOCK_END scheduling. After the patch, that branch first calls verify_ticks(block); on failure it calls handle_bad_block(sched, block), emits FD_SCHED_TT_MARK_DEAD for the bank, and returns. Before the patch, fd_ssload_recover() used DEFAULT_HASHES_PER_TICK when the snapshot manifest lacked hashes_per_tick. After the patch, it uses 0UL with a comment that None is treated as 0 for hash verification. The parser also adds a bound check for mblk_cnt before consuming another microblock.

# Root Cause

The supported root cause is an incomplete or incorrectly parameterized replay validation boundary: the supplied before-code shows no tick verification gate immediately before normal block-end scheduling, and snapshot recovery initialized missing hashes_per_tick with a default value rather than the documented 0UL value used for verification.

## Walkthrough

1. Snapshot recovery initializes bank replay parameters, including hashes_per_tick.

2. Previously, a missing manifest hashes_per_tick value was mapped to DEFAULT_HASHES_PER_TICK.

3. The patch maps that missing value to 0UL and documents that this matches hash verification behavior.

4. Replay parsing tracks microblocks and tick-related counters used later by validation.

5. The patch adds a maximum microblock-count check before parsing another microblock.

6. When block_should_signal_end(block) is true, the scheduler reaches the block completion path.

7. Previously, the provided evidence shows that path emitting FD_SCHED_TT_BLOCK_END directly.

8. After the patch, the scheduler calls verify_ticks(block) before normal block-end handling.

9. If verification fails, the block is handled as bad and the bank is marked dead instead of completing normally.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/replay/fd_sched.c | 1061 | block completion scheduling now verifies ticks before accepting block end and marks bad blocks dead |
| src/discof/restore/utils/fd_ssload.c | 112 | snapshot manifest recovery sets hashes_per_tick baseline used by PoH hash verification |
| src/discof/replay/fd_sched.c | 1692 | microblock parsing path tracks and bounds microblocks feeding tick/PoH validation |

## Code Snippets

## Snippet 1

Context: `src/discof/restore/utils/fd_ssload.c:112` (changes signature or replay validation logic)

Before
```c
rent->burn_percent            = manifest->rent_params.burn_percent;

  if( FD_LIKELY( manifest->has_hashes_per_tick ) ) fd_bank_hashes_per_tick_set( bank, manifest->hashes_per_tick );
  else                                             fd_bank_hashes_per_tick_set( bank, DEFAULT_HASHES_PER_TICK );

  fd_lthash_value_t * lthash = fd_bank_lthash_locking_modify( bank );
```
After
```c
rent->burn_percent            = manifest->rent_params.burn_percent;

  /* https://github.com/anza-xyz/agave/blob/v3.0.6/ledger/src/blockstore_processor.rs#L1118
     None gets treated as 0 for hash verification. */
  if( FD_LIKELY( manifest->has_hashes_per_tick ) ) fd_bank_hashes_per_tick_set( bank, manifest->hashes_per_tick );
  else                                             fd_bank_hashes_per_tick_set( bank, 0UL );

  fd_lthash_value_t * lthash = fd_bank_lthash_locking_modify( bank );
```

## Snippet 2

Context: `src/discof/replay/fd_sched.c:1061` (changes a sensitive control or state-update path)

Before
```c
if( FD_UNLIKELY( block_should_signal_end( block ) ) ) {
    FD_TEST( block->block_start_signaled );
    out->task_type = FD_SCHED_TT_BLOCK_END;
    out->block_end->bank_idx = bank_idx;
```
After
```c
if( FD_UNLIKELY( block_should_signal_end( block ) ) ) {
    FD_TEST( block->block_start_signaled );
    if( FD_UNLIKELY( verify_ticks( block ) ) ) {
      /* Tick verification can't be done at parse time, because we may
         not know the expected number of hashes yet.  It can't be driven
         by transaction dispatch/completion, because the block may be
         empty.  Similary, it can't be driven by PoH hashing, because a
         bad block may simply not have any microblocks. */
```

## Snippet 3

Context: `src/discof/replay/fd_sched.c:1762` (changes a sensitive control or state-update path)

Before
```c
block->mblks_rem     = FD_LOAD( ulong, block->fec_buf );
      block->fec_buf_soff += (uint)sizeof(ulong);
      /* FIXME what happens if someone sends us mblks_rem==0UL here? */

      block->fec_sob = 0;
```
After
```c
block->mblks_rem     = FD_LOAD( ulong, block->fec_buf );
      block->fec_buf_soff += (uint)sizeof(ulong);

      block->fec_sob = 0;
```

## Snippet 4

Context: `src/discof/replay/fd_sched.c:1692` (changes signature or replay validation logic)

Before
```c
}
    if( block->txns_rem==0UL && block->mblks_rem>0UL ) {
      CHECK_LEFT( sizeof(fd_microblock_hdr_t) );
      fd_microblock_hdr_t * hdr = (fd_microblock_hdr_t *)fd_type_pun( block->fec_buf+block->fec_buf_soff );
      block->fec_buf_soff      += (uint)sizeof(fd_microblock_hdr_t);

      memcpy( block->poh.hash, hdr->hash, sizeof(block->poh.hash) );
      block->txns_rem = hdr->txn_cnt;
```
After
```c
}
    if( block->txns_rem==0UL && block->mblks_rem>0UL ) {
      if( FD_UNLIKELY( block->mblk_cnt>=FD_SCHED_MAX_MBLK_PER_SLOT ) ) {
        /* A valid block shouldn't contain more than this amount of
           microblocks. */
        FD_LOG_INFO(( "bad block: slot %lu, parent slot %lu, mblk_cnt %u (%u ticks) >= %lu", block->slot, block->parent_slot, block->mblk_cnt, block->mblk_tick_cnt, FD_SCHED_MAX_MBLK_PER_SLOT ));
        return FD_SCHED_PARSER_BAD_BLOCK;
      }
```

# Fix Pattern

Add a replay validation gate at the block completion boundary, align recovered hashes_per_tick state with reference verification semantics, and reject parser states that exceed the expected microblock bound.

## How It Was Fixed

fd_sched_task_next_ready() now invokes verify_ticks(block) before producing FD_SCHED_TT_BLOCK_END. Failure calls handle_bad_block(sched, block), sets FD_SCHED_TT_MARK_DEAD, records the bank index, and returns. fd_ssload_recover() now sets hashes_per_tick to 0UL when the manifest omits the value. fd_sched_parse() now rejects blocks whose microblock count reaches FD_SCHED_MAX_MBLK_PER_SLOT before another microblock is parsed.

# Why It Matters

1. Adds an explicit PoH/tick validation gate before replay block completion.

2. Prevents malformed tick structure from taking the normal block-end path in the shown scheduler branch.

3. Keeps snapshot-derived hashes_per_tick semantics consistent with later verification.

4. Consensus/replay validation is security-sensitive even without a demonstrated exploit.

# Evidence Notes

Evidence supports replay/consensus validation, not cryptographic signature validation. There is no supplied proof of attacker capability, remote exploitability, signature forgery, authorization bypass, or finalized invalid consensus state. The removed FIXME is not treated as root-cause evidence. The parser bound is supporting hardening unless tied directly to verify_ticks by code not shown. Protocol security invariant: During replay, normal block-end handling should not proceed unless the block's tick/PoH structure is consistent with the bank's hashes_per_tick semantics, including the snapshot case where a missing hashes_per_tick value is treated as 0 for verification. Verification notes: No concrete exploit path or attacker capability is proven by the patch evidence. No proof is shown that invalid PoH previously reached finalized consensus state in all configurations. No signature forgery, cryptographic primitive weakness, or transaction authorization bypass is shown. The removed FIXME alone is not evidence of a security fix. Confirmed from provided snippets: verify_ticks(block) was inserted before block-end scheduling. Confirmed from provided snippets: failed verification marks the bank dead rather than emitting normal block end. Confirmed from provided snippets: missing hashes_per_tick changed from DEFAULT_HASHES_PER_TICK to 0UL. Not established by provided evidence: a concrete exploit path or prior finalized invalid state. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-poh-validation`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, validator, consensus, replay, poh, tick-verification, snapshot`

The supplied patch evidence supports keeping this as security hardening, not a fully proven security fix. The strongest change inserts PoH/tick verification before normal block-end scheduling and marks the bank/block dead on failure, which clearly tightens a consensus-sensitive validation boundary. The snapshot hashes_per_tick change also aligns recovered state with verification semantics. However, the evidence does not prove attacker capability, exploitability, request forgery, signature validation failure, or finalized invalid consensus state, so the original cryptography/signature/replay-forgery framing is too strong.

## Security Evidence

1. Block completion now calls verify_ticks(block) before emitting the normal block-end task.
2. Failed tick verification calls handle_bad_block and emits FD_SCHED_TT_MARK_DEAD instead of completing the block normally.
3. Snapshot recovery changes missing hashes_per_tick from DEFAULT_HASHES_PER_TICK to 0UL with an explicit verification-semantics comment.
4. Parser adds a bound check rejecting excessive microblock count as a bad block in a replay path.
5. Commit subject says replay/scheduler PoH verification, matching the validation-sensitive code changes.

## Missing Evidence

1. No concrete exploit path or attacker-controlled input flow is shown.
2. No proof that invalid PoH or tick structure previously reached finalized consensus state is supplied.
3. No evidence of signature forgery, transaction authorization bypass, or cryptographic primitive weakness is shown.
4. No test output or regression case demonstrating the prior security failure is included.

## Claim Boundaries

1. Classify as consensus/PoH validation hardening rather than signature or cryptographic validation.
2. Do not claim request forgery or replay attack impact from the supplied evidence alone.
3. Do not claim a confirmed exploitable vulnerability without attacker capability and impact evidence.
4. The removed FIXME is not meaningful security evidence by itself.
