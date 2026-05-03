---
case_id: case_20240319_863698b5d
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2024-03-19
source_refs:
  - git:863698b5df52213ed40d29bee3089bc7d0ca6b95
  - "src/app/fdctl/run/tiles/fd_poh.c:374"
  - "src/app/fdctl/run/tiles/fd_poh.c:955"
  - "src/app/fdctl/run/tiles/fd_poh.c:933"
  - "src/app/fdctl/run/tiles/fd_poh.c:967"
bug_class: consensus-liveness-failure
impact_type:
  - consensus-liveness
confidence: medium
tags:
  - blockchain-core
  - consensus
  - validator
  - poh
  - leader-transition
  - skipped-slots
  - liveness
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a PoH leader transition bug after skipped slots. Before the fix, the validator could produce the first leader slot after skipped slots but leave that bank with an incorrect tick height, causing replay to treat it as incomplete and repeatedly fork later slots from the older parent. The change records recent tick hashes while not leader and registers skipped ticks when leadership begins. The evidence supports a consensus/liveness correctness fix, but does not establish a concrete security exploit, remote attack path, funds impact, or network-wide safety violation.

## Observed Patch Facts

1. In `src/app/fdctl/run/tiles/fd_poh.c`, the patch replaces `/* The timestamp in nanoseconds of when the reset slot was received.` with `/* When we are not leader, we need to save the hashes that were`.

2. In `src/app/fdctl/run/tiles/fd_poh.c`, the patch replaces `if( FD_UNLIKELY( is_leader && ctx->hashcnt>=(ctx->next_leader_slot_hashcnt+ctx->hashc...` with `if( FD_UNLIKELY( !is_leader && !(ctx->hashcnt%ctx->hashcnt_per_tick) ) ) {`.

3. In `src/app/fdctl/run/tiles/fd_poh.c`, the patch replaces `if( FD_UNLIKELY( is_leader && !(ctx->hashcnt%ctx->hashcnt_per_tick) ) ) {` with `if( FD_UNLIKELY( !is_leader && ctx->hashcnt>=ctx->next_leader_slot_hashcnt ) ) {`.

4. In `src/app/fdctl/run/tiles/fd_poh.c`, the patch adds `break;`.

## Project Context

The changed code sits primarily in `src/app/fdctl/run/tiles`, `src/app/fdctl/run`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/app/fdctl/run/tiles/tiles.h`, `src/app/fdctl/run/tiles/fd_verify.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/app/fdctl/run/tiles/tiles.h`, `src/app/fdctl/run/tiles/fd_verify.c`. The strongest project-level identifiers around this patch are `leader`, `hashcnt`, `hash`, and `hashes`.

## Before/After Behavior

Before the patch, non-leader tick hashes were not retained for later bank registration, and the commit message states that after skipped slots the validator built slot 104 on parent 99 but then kept building slots 105 and later on parent 99 because the slot 104 bank was not complete. After the patch, `skipped_tick_hashes[150][32]` stores recent non-leader tick hashes, tick boundaries while not leader are copied into that ring buffer, and the transition into leadership registers skipped ticks on `current_leader_bank` before production continues. A `break` was also added after leaving leader state.

# Root Cause

The pre-patch PoH path did not reconstruct/register ticks for slots skipped by a previous leader before the validator began producing as leader. This left the new leader bank's tick height inconsistent with the expected skipped-slot progression, so `bank.is_complete()` could remain false. Because recent slot hashes are exposed through a consensus-visible sysvar, the fix needed to preserve recent tick hashes rather than use arbitrary values for all skipped ticks.

## Walkthrough

1. A validator is scheduled to become leader after another validator skips one or more slots.

2. PoH continues advancing while the validator is not leader, but pre-patch evidence does not show the relevant non-leader tick hashes being saved for later bank registration.

3. When the validator becomes leader, it can initially build on the correct pre-skip parent.

4. The commit message says the produced bank then has the wrong tick height, causing `bank.is_complete()` to return false.

5. Replay does not treat that bank as a valid parent for the next slot, so the validator repeatedly creates new forks from the old parent.

6. The patch saves non-leader tick hashes at tick boundaries in a 150-entry ring buffer.

7. On non-leader-to-leader transition, the patch registers skipped ticks from `reset_slot_hashcnt` to `next_leader_slot_hashcnt` on the current leader bank.

8. This advances bank tick height and preserves recent consensus-visible slot hash values within the stated 150-entry window.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/app/fdctl/run/tiles/fd_poh.c | 374 | adds skipped_tick_hashes ring buffer for consensus-visible skipped tick hashes |
| src/app/fdctl/run/tiles/fd_poh.c | 933 | on transition from non-leader to leader, registers ticks for skipped slots into the current leader bank |
| src/app/fdctl/run/tiles/fd_poh.c | 955 | records tick hashes while not leader so skipped leader slots can be replayed later |
| src/app/fdctl/run/tiles/fd_poh.c | 967 | breaks after leaving leader state to avoid continuing an invalid production loop |

## Code Snippets

## Snippet 1

Context: `src/app/fdctl/run/tiles/fd_poh.c:374` (changes signature or replay validation logic)

Before
```c
uchar __attribute__((aligned(32UL))) hash[ 32 ];

  /* The timestamp in nanoseconds of when the reset slot was received.
     This is the timestamp we are building on top of to determine when
```
After
```c
uchar __attribute__((aligned(32UL))) hash[ 32 ];

  /* When we are not leader, we need to save the hashes that were
     produced in case the prior leader skips.  If they skip, we will
     replay these skipped hashes into our next leader bank so that
     the slot hashes sysvar can be updated correctly.  We only need 150
     of these, because that's what's required for consensus in the
     sysvar. */
```

## Snippet 2

Context: `src/app/fdctl/run/tiles/fd_poh.c:955` (changes signature or replay validation logic)

Before
```c
}

    if( FD_UNLIKELY( is_leader && ctx->hashcnt>=(ctx->next_leader_slot_hashcnt+ctx->hashcnt_per_slot) ) ) {
      /* We ticked while leader and are no longer leader... transition
```
After
```c
}

    if( FD_UNLIKELY( !is_leader && !(ctx->hashcnt%ctx->hashcnt_per_tick) ) ) {
      /* We ticked while not leader... save the current hash so it can
         be played back into the bank (to update the recent slot hashes
         sysvar) when we become the leader. */
      fd_memcpy( ctx->skipped_tick_hashes[ (ctx->hashcnt/ctx->hashcnt_per_tick)%150UL ], ctx->hash, 32UL );
    }
```

## Snippet 3

Context: `src/app/fdctl/run/tiles/fd_poh.c:933` (changes a sensitive control or state-update path)

Before
```c
ctx->hashcnt++;

    if( FD_UNLIKELY( is_leader && !(ctx->hashcnt%ctx->hashcnt_per_tick) ) ) {
      /* We ticked while leader... tell the leader bank. */
```
After
```c
ctx->hashcnt++;

    if( FD_UNLIKELY( !is_leader && ctx->hashcnt>=ctx->next_leader_slot_hashcnt ) ) {
      /* We were not leader but became leader... we need to register ticks on the
         bank for all of the slots that were skipped. */
      for( ulong skipped_hashcnt=ctx->reset_slot_hashcnt; skipped_hashcnt<ctx->next_leader_slot_hashcnt; skipped_hashcnt+=ctx->hashcnt_per_tick ) {
        /* The "hash" value we provide doesn't matter for all but the
           oldest 150 ticks, since only the most recent 150 ticks are
```

## Snippet 4

Context: `src/app/fdctl/run/tiles/fd_poh.c:967` (changes a sensitive control or state-update path)

Before
```c
FD_TEST( !max_remaining_microblocks );
      no_longer_leader( ctx );
    }
```
After
```c
FD_TEST( !max_remaining_microblocks );
      no_longer_leader( ctx );
      break;
    }
```

# Fix Pattern

Carry bounded consensus-visible PoH tick state across skipped-slot leader transitions, then replay/register skipped ticks into the leader bank before producing as leader.

## How It Was Fixed

The fix adds `skipped_tick_hashes[150][32]` to the PoH context, records the current PoH hash into that ring buffer whenever a non-leader tick boundary is reached, and registers skipped ticks into `current_leader_bank` when `hashcnt >= next_leader_slot_hashcnt` while not leader. The 150-entry bound is justified in the commit message by the recent slot hash sysvar window. The patch also stops the loop after `no_longer_leader(ctx)` by adding a `break`.

# Why It Matters

1. Pre-patch behavior could cause repeated local forks after skipped leader slots.

2. The issue affects validator consensus/liveness behavior in the PoH leader path.

3. The supplied evidence does not prove transaction validation bypass, authorization bypass, theft, or direct account-state corruption.

4. The security relevance is plausible because the code is consensus-sensitive, but the vulnerability thesis is not established by the provided evidence.

# Evidence Notes

Primary evidence is limited to `src/app/fdctl/run/tiles/fd_poh.c`. The diff adds a skipped tick hash ring buffer, records non-leader tick hashes, registers skipped ticks on transition to leader, and adds a loop break after leaving leader state. The commit message provides the concrete failure scenario and explains the wrong bank tick height. Claims about signature validation, cryptographic replay validation, remote exploitability, funds impact, or direct protocol safety failure are unsupported and have been removed. Protocol security invariant: A validator that becomes leader after skipped slots must register the skipped tick progression into its leader bank and preserve consensus-visible recent slot hash values so the bank can be considered complete and subsequent slots build on the newly produced slot. Verification notes: No remote exploit path is proven by the patch evidence. No transaction signature, authorization, or account-state validation bypass is shown. No funds theft or direct integrity compromise is demonstrated. The evidence supports validator consensus/liveness failure, not necessarily a network-wide chain safety break. The 150-slot bound is justified by the sysvar consensus window in the commit message, but no independent spec proof is included. No tests or runtime verification are included in the provided input. The 150-entry consensus window is supported only by the commit message and code comments, not by an independently provided spec. Security classification is downgraded because the evidence establishes a liveness/correctness bug but not a demonstrated vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-liveness-failure`
Final impact type: `consensus-liveness`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, validator, poh, leader-transition, skipped-slots, liveness`

The evidence supports a consensus-sensitive hardening case rather than a proven exploitable security fix. The patch handles skipped-slot leader transitions by preserving and replaying recent tick hashes so the leader bank reaches the expected tick height and consensus-visible sysvar state remains correct. The supplied evidence does not prove theft, signature replay, transaction forgery, or a network-wide safety break, but it does show removal of an exposed validator consensus/liveness failure mode triggered by skipped leader slots.

## Security Evidence

1. Patch changes PoH leader-transition logic in validator code.
2. Commit describes infinite forking after a previous leader skipped slots.
3. Code comments state recent slot hashes are exposed through a consensus-critical sysvar.
4. Patch records non-leader tick hashes and registers skipped ticks when leadership begins.
5. Fix is bounded to the recent 150-slot consensus-visible window.

## Missing Evidence

1. No demonstrated remote exploit path beyond skipped-slot conditions.
2. No evidence of transaction forgery, signature bypass, or replay attack.
3. No proof of funds loss or direct account-state corruption.
4. No independent protocol spec or test evidence validating the 150-slot bound.
5. No evidence that the bug causes network-wide consensus safety failure rather than local validator liveness failure.

## Claim Boundaries

1. Classify as consensus/liveness hardening, not a concrete vulnerability fix.
2. Do not claim request forgery, signature replay, or authorization bypass.
3. Do not claim direct financial impact from the supplied patch evidence.
4. Do not claim all skipped-slot scenarios are adversarial, only that skipped slots are an exposed consensus condition.
5. Security relevance rests on validator consensus-critical PoH/sysvar behavior, not on cryptographic primitive weakness.
