---
case_id: case_20260223_3e0535b19
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2026-02-23
source_refs:
  - git:3e0535b190d0fc0f9ef002546132b9afb4b33c15
  - "src/discof/replay/fd_sched.c:1760"
  - "src/discof/replay/fd_sched.c:1695"
  - "src/discof/replay/fd_sched.c:1339"
  - "src/discof/replay/fd_sched.c:1829"
bug_class: malformed-block-resource-exhaustion
impact_type:
  - denial-of-service
  - resource-exhaustion
confidence: medium
tags:
  - blockchain-core
  - replay
  - poh
  - tick-verification
  - resource-control
  - integer-overflow
  - malformed-input
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security fix for malformed-block resource exhaustion in Firedancer's replay PoH scheduler. The patch makes tick/hash validation eager in scheduler progress paths and changes curr_tick_hashcnt accumulation from ordinary unsigned addition to saturating addition, preventing overflow from hiding excessive hash counts. The evidence does not support broader claims about signature validation, access control, memory corruption, or proven consensus divergence.

## Observed Patch Facts

1. In `src/discof/replay/fd_sched.c`, the patch replaces `if( FD_UNLIKELY( block->hashes_per_tick>1UL && (block->hashes_per_tick!=block->prev_t...` with `return verify_ticks_eager( block );`.

2. In `src/discof/replay/fd_sched.c`, the patch replaces `/* https://github.com/anza-xyz/agave/blob/v3.0.6/ledger/src/blockstore_processor.rs#L...` with `/* Agave invokes verify_ticks() anywhere between once per slot and once`.

3. In `src/discof/replay/fd_sched.c`, the patch replaces `FD_TEST( block->hashes_per_tick!=ULONG_MAX );` with `if( FD_UNLIKELY( verify_ticks_eager( block ) ) ) {`.

4. In `src/discof/replay/fd_sched.c`, the patch replaces `block->curr_tick_hashcnt += hdr->hash_cnt; /* For tick_verify, take the number of has...` with `block->curr_tick_hashcnt = fd_ulong_sat_add( hdr->hash_cnt, block->curr_tick_hashcnt...`.

## Project Context

The changed code sits primarily in `src/discof/replay`, `src/discof`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/discof/replay/fd_sched.h`, `src/discof/replay/fd_replay_tile.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/discof/replay/fd_sched.h`, `src/discof/replay/fd_replay_tile.c`. The strongest project-level identifiers around this patch are `block`, `hashes_per_tick`, `hashing`, and `slot`. Nearby tests or test-like files include `src/discof/backtest/fd_blockstore2shredcap.c`, `src/discof/restore/utils/fuzz_slot_delta_parser.c`.

## Before/After Behavior

Before the patch, fd_sched_parse accumulated block->curr_tick_hashcnt with wrapping unsigned addition from hdr->hash_cnt, and some tick/hash checks were performed through local or final verification paths. A sufficiently large sequence of hash_cnt values could overflow the cumulative counter before later bounds checks. After the patch, curr_tick_hashcnt uses fd_ulong_sat_add, task completion calls verify_ticks_eager(block) and rejects bad blocks through handle_bad_block, and final verify_ticks delegates to verify_ticks_eager(block) after trailing-entry validation.

# Root Cause

Replay scheduler tick/hash accounting allowed malformed microblock hash counts to be accumulated with wrapping arithmetic and did not consistently apply the relevant tick/hash bounds checks through the eager verification path soon enough to bound replay work.

## Walkthrough

1. Replay parses microblock headers and reads hdr->hash_cnt from block data.

2. For tick verification, hdr->hash_cnt is added into block->curr_tick_hashcnt verbatim.

3. Before the fix, that cumulative update used normal unsigned addition, so excessive values could wrap.

4. The scheduler allows parsing and out-of-order work ahead of full slot completion, so delayed validation can leave room for bogus tick/hash counts to consume compute cycles.

5. The patch changes curr_tick_hashcnt accumulation to fd_ulong_sat_add, preserving an overflowed state as a large saturated value instead of wrapping low.

6. The task completion path now calls verify_ticks_eager(block) and rejects via handle_bad_block on failure.

7. The final verify_ticks path also calls verify_ticks_eager(block), aligning final validation with the eager check path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/replay/fd_sched.c | 1339 | Calls verify_ticks_eager after hashing task completion and rejects bad blocks before continuing replay work. |
| src/discof/replay/fd_sched.c | 1695 | Documents eager tick verification rationale for out-of-order replay scheduling and compute-cycle mitigation. |
| src/discof/replay/fd_sched.c | 1760 | Final verify_ticks path now delegates to verify_ticks_eager after trailing-entry validation. |
| src/discof/replay/fd_sched.c | 1829 | Accumulates curr_tick_hashcnt with fd_ulong_sat_add to avoid unsigned overflow in tick hash counting. |

## Code Snippets

## Snippet 1

Context: `src/discof/replay/fd_sched.c:1760` (changes a sensitive control or state-update path)

Before
```c
return -1;
  }
  if( FD_UNLIKELY( block->hashes_per_tick>1UL && (block->hashes_per_tick!=block->prev_tick_hashcnt||block->inconsistent_hashes_per_tick) ) ) {
    /* >1 since we don't care about checking low power hashing or
       hashing disabled. */
    FD_LOG_INFO(( "bad block: INVALID_TICK_HASH_COUNT, slot %lu, parent slot %lu, expected %lu, got %lu", block->slot, block->parent_slot, block->hashes_per_tick, block->prev_tick_hashcnt ));
    return -1;
  }
```
After
```c
return -1;
  }

  return verify_ticks_eager( block );
}
```

## Snippet 2

Context: `src/discof/replay/fd_sched.c:1695` (changes an authorization or privilege gate)

Before
```c
}

/* https://github.com/anza-xyz/agave/blob/v3.0.6/ledger/src/blockstore_processor.rs#L1057

   Returns 0 on success. */
static int
verify_ticks( fd_sched_block_t * block ) {
  FD_TEST( block->fec_eos );
```
After
```c
}

/* Agave invokes verify_ticks() anywhere between once per slot and once
   per entry batch, before tranactions are parsed or dispatched for
   execution.  We can't do quite the same thing due to out-of-order
   scheduling and the fact that we allow parsing to run well ahead of
   block boundaries.  Out-of-order scheduling is good, so is overlapping
   parsing with execution.  The easiest thing for us would be to just
```

## Snippet 3

Context: `src/discof/replay/fd_sched.c:1339` (changes bounds, limits, or capacity handling)

Before
```c
mblk_in_progress_slist_idx_push_tail( block->mblks_hashing_in_progress, msg->mblk_idx, block->mblk_in_progress_pool );
      }
      FD_TEST( block->hashes_per_tick!=ULONG_MAX );
      if( FD_UNLIKELY( block->curr_tick_hashcnt>block->hashes_per_tick && block->hashes_per_tick>1UL ) ) { /* >1 to ignore low power hashing or no hashing cases */
        /* We couldn't really check this at parse time because we may
           not have the expected hashes per tick value yet.  We couldn't
           delay this till after all PoH hashing is done, because this
           would be a DoS vector.  This is a good place to do the check.
```
After
```c
mblk_in_progress_slist_idx_push_tail( block->mblks_hashing_in_progress, msg->mblk_idx, block->mblk_in_progress_pool );
      }
      if( FD_UNLIKELY( verify_ticks_eager( block ) ) ) {
        handle_bad_block( sched, block );
        return -1;
```

## Snippet 4

Context: `src/discof/replay/fd_sched.c:1829` (changes a sensitive control or state-update path)

Before
```c
We implement the above for consensus. */
      mblk->hashcnt = fd_ulong_sat_sub( hdr->hash_cnt, fd_ulong_if( !hdr->txn_cnt, 0UL, 1UL ) ); /* For pure hashing, implement the above. */
      block->curr_tick_hashcnt += hdr->hash_cnt; /* For tick_verify, take the number of hashes verbatim. */
      block->hashcnt += mblk->hashcnt+fd_ulong_if( !hdr->txn_cnt, 0UL, 1UL );
      memcpy( mblk->end_hash, hdr->hash, sizeof(fd_hash_t) );
```
After
```c
We implement the above for consensus. */
      mblk->hashcnt = fd_ulong_sat_sub( hdr->hash_cnt, fd_ulong_if( !hdr->txn_cnt, 0UL, 1UL ) ); /* For pure hashing, implement the above. */
      block->curr_tick_hashcnt = fd_ulong_sat_add( hdr->hash_cnt, block->curr_tick_hashcnt ); /* For tick_verify, take the number of hashes verbatim. */
      block->hashcnt += mblk->hashcnt+fd_ulong_if( !hdr->txn_cnt, 0UL, 1UL );
      memcpy( mblk->end_hash, hdr->hash, sizeof(fd_hash_t) );
```

# Fix Pattern

Apply eager validation to resource-controlling protocol counters and use saturating arithmetic for cumulative counters whose wraparound could defeat later bounds checks.

## How It Was Fixed

The patch replaces wrapping curr_tick_hashcnt accumulation with fd_ulong_sat_add, replaces a local task-completion hash-count check with verify_ticks_eager(block), and makes final verify_ticks call verify_ticks_eager(block) after trailing-entry validation. The added comment explicitly frames eager tick/hash checks as mitigation for bogus counts causing runaway compute-cycle consumption.

# Why It Matters

1. Malformed block data can otherwise force unnecessary replay hashing or scheduler work before rejection.

2. Unsigned overflow can make an excessive cumulative hash count appear acceptable to later validation.

3. The supported impact is resource exhaustion in replay/PoH handling, not signature forgery, access-control bypass, or memory corruption.

# Evidence Notes

Primary evidence is limited to src/discof/replay/fd_sched.c. The strongest points are the commit body stating "Constrain tick count" and "Fix an overflow in hashcnt accumulation", the change from block->curr_tick_hashcnt += hdr->hash_cnt to fd_ulong_sat_add, the replacement of the task-completion local check with verify_ticks_eager(block), and comments stating that delaying verification can allow bogus tick and hash counts to cause runaway compute-cycle consumption. Heuristic claims about access control, generic cryptography, or replay-signature validation are unsupported and should be ignored. Protocol security invariant: During replay, PoH tick and hash counts taken from block microblock headers must be bounded early enough that malformed block data cannot drive unbounded hashing or scheduling work, and cumulative hash-count accounting must not wrap around into an apparently valid smaller value. Verification notes: No proof of memory corruption is shown by the patch. No proof of signature forgery or replay-authentication bypass is shown. No access-control or privilege-check invariant is evidenced despite heuristic labeling. No concrete remote exploit path is proven beyond malformed block-driven resource consumption risk. No consensus divergence claim is proven, though replay validity checks are involved. No exploit proof is provided, so the verdict is likely rather than confirmed. No evidence shows memory corruption, privilege escalation, signature forgery, or access-control bypass. No helper files appear to be the root cause in the provided evidence. The finding is grounded in malformed block-driven replay resource control and integer overflow prevention. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `malformed-block-resource-exhaustion`
Final impact type: `denial-of-service, resource-exhaustion`
Final confidence: `medium`
Final tags: `blockchain-core, replay, poh, tick-verification, resource-control, integer-overflow, malformed-input`

The supplied patch evidence supports retaining this as security hardening for malformed-block resource exhaustion in replay/PoH tick verification. The strongest evidence is the added rationale explicitly describing bogus tick and hash counts causing runaway compute-cycle consumption, the replacement of delayed/local checks with eager verification, and the change from wrapping unsigned accumulation to saturating addition. The original replay/signature-validation and request-forgery/replay framing is too strong; the supported issue is resource-control hardening against malformed block data, not forgery, access control, or proven consensus compromise.

## Security Evidence

1. Commit body says it constrains tick count and fixes overflow in hashcnt accumulation.
2. Added comments state delayed verification can allow bogus tick and hash counts to cause runaway compute-cycle consumption.
3. Task completion now calls verify_ticks_eager and rejects bad blocks via handle_bad_block.
4. curr_tick_hashcnt accumulation changed from ordinary unsigned addition to fd_ulong_sat_add, preventing wraparound from hiding excessive counts.
5. Changed code is in replay scheduler handling block microblock hash/tick counts.

## Missing Evidence

1. No proof of a concrete exploit path or attacker-controlled delivery boundary beyond malformed block data is shown.
2. No evidence supports signature forgery, replay-authentication bypass, or access-control impact.
3. No test, advisory, or vulnerability reference is provided.
4. No demonstrated consensus divergence or network-wide impact is proven from the patch alone.

## Claim Boundaries

1. Classify as malformed-block resource exhaustion hardening, not cryptographic signature validation.
2. Supported impact is denial of service or excess compute consumption only.
3. Do not claim memory corruption, privilege escalation, request forgery, or replay forgery.
4. Confidence should be medium because security intent is explicit, but exploitability is not demonstrated.
