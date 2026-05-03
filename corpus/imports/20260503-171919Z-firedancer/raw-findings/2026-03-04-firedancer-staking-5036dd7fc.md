---
case_id: case_20260304_5036dd7fc
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: staking
confidence: medium
source_quality: high
date: 2026-03-04
source_refs:
  - git:5036dd7fcddde0acd1f415aa88bb6baacd65144f
  - "src/flamenco/stakes/fd_vote_stakes.h:142"
  - "src/flamenco/runtime/fd_runtime.c:602"
  - "src/flamenco/rewards/fd_rewards.c:467"
  - "src/flamenco/rewards/fd_rewards.c:375"
bug_class: bounds-check-hardening
impact_type:
  - memory-safety
tags:
  - blockchain-core
  - staking
  - rewards
  - bounds-check
  - memory-safety
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded security-relevant change is in Firedancer reward calculation. The pre-patch code directly indexed `runtime_stack->stakes.stake_points_result[ stake_delegation->idx ]` in the partitioned reward path, while the patched code checks `stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS` and uses a local result buffer for out-of-capacity delegations. This supports a likely security-hardening classification for bounds safety in a consensus-sensitive rewards path, but not a confirmed externally exploitable vulnerability.

## Observed Patch Facts

1. In `src/flamenco/stakes/fd_vote_stakes.h`, the patch replaces `/* Below are the APIs for inserting elements into the vote stakes object` with `/* fd_vote_stakes_root_{insert, update, purge}_key are APIs for`.

2. In `src/flamenco/runtime/fd_runtime.c`, the patch replaces `/* We want to cache the stake values for T-1 and T-2 in the forward` with `/* Now that our stakes caches have been updated, we can calculate the`.

3. In `src/flamenco/rewards/fd_rewards.c`, the patch replaces `if( FD_UNLIKELY( vote_ele[idx].invalid ) ) continue;` with `fd_calculated_stake_points_t stake_points_result_[1];`.

4. In `src/flamenco/rewards/fd_rewards.c`, the patch replaces `FD_TEST( idx!=UINT_MAX );` with `if( FD_UNLIKELY( idx==UINT_MAX ) ) continue;`.

## Project Context

The changed code sits primarily in `src/flamenco/stakes`, `src/flamenco`, `src/flamenco/runtime`, which anchors the finding in the `staking` area of the project. Historical context from `src/flamenco/stakes/fd_stake_delegations.h`, `src/flamenco/stakes/test_stake_delegations.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/flamenco/stakes/fd_stake_delegations.h`, `src/flamenco/runtime/test_bank.c`. The strongest project-level identifiers around this patch are `stake`, `stake_delegation`, `elements`, and `fd_calculated_stake_points_t`. Nearby tests or test-like files include `src/flamenco/runtime/fuzz_genesis_parse.c`, `src/flamenco/runtime/tests/test_dump_block.c`.

## Before/After Behavior

Before the patch, `calculate_reward_points_partitioned` asserted that a vote-map entry existed and then used `stake_delegation->idx` directly to select an element of the fixed `runtime_stack->stakes.stake_points_result` cache. The supplied evidence shows no bounds guard before that index. After the patch, missing vote-map entries are skipped, and delegations whose index is outside `FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS` use a local `fd_calculated_stake_points_t` result instead of the fixed cache. In `calculate_stake_vote_rewards`, the patched code also recalculates stake points when the delegation index cannot safely use the cache. The epoch and vote-stakes changes provide surrounding staking context but are not independently shown to be security fixes.

# Root Cause

The supported root cause is an unsafe assumption that `stake_delegation->idx` was always valid for the fixed-size `runtime_stack->stakes.stake_points_result` cache. The evidence does not establish the full conditions under which such an out-of-capacity index arises or any external exploit path.

## Walkthrough

1. Reward calculation iterates stake delegations and looks up each delegation's vote account in `vote_ele_map`.

2. In the pre-patch partitioned path, a missing vote-map entry triggered `FD_TEST( idx!=UINT_MAX )`; the patched path skips when `idx==UINT_MAX`.

3. The pre-patch partitioned path directly formed `&runtime_stack->stakes.stake_points_result[ stake_delegation->idx ]`.

4. The patched path introduces a local `fd_calculated_stake_points_t` result and selects it when `stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS`.

5. The non-partitioned stake vote reward path also recalculates stake points when recalculation is requested or when the delegation index is outside the fixed cache capacity.

6. Header/comment and epoch-cache changes indicate broader staking/rewards decoupling, but the concrete security-relevant evidence is the reward-cache bounds handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/rewards/fd_rewards.c | 375 | partitioned reward point calculation now avoids asserting missing vote map entries and avoids indexing stake_points_result when stake_delegation->idx is out of fixed-cache bounds |
| src/flamenco/rewards/fd_rewards.c | 467 | stake vote reward calculation recalculates stake points when rewards are recalculated or the delegation index cannot safely use the cached stake_points_result array |
| src/flamenco/runtime/fd_runtime.c | 602 | epoch transition staking cache update path feeding leader schedule and reward-related stake state |
| src/flamenco/stakes/fd_vote_stakes.h | 142 | root fork vote-stake snapshot loading APIs for T-1 and T-2 stake sets |

## Code Snippets

## Snippet 1

Context: `src/flamenco/stakes/fd_vote_stakes.h:142` (changes a consensus- or validator-sensitive branch)

Before
```c
fd_vote_stakes_join( void * shmem );

/* Below are the APIs for inserting elements into the vote stakes object
   at boot.  It's possible that the insertion of elements happens
   disjointly.  The caller is able to insert elements in any order and
   then assign stake/node account values to elements that are already
   inserted.  After all elements are inserted, fd_vote_stakes_fini_root
   is called to finalize the root fork.  The caller is responsible for
```
After
```c
fd_vote_stakes_join( void * shmem );

/* fd_vote_stakes_root_{insert, update, purge}_key are APIs for
   inserting, updating, and purging keys for the root fork.  These
   operations are split out in order to support the snapshot loading
   process.  The set of stakes from the T-1 epoch are inserted into
   the root fork with a call to fd_vote_stakes_root_insert_key.  The
   set of stakes from the T-2 epoch are updated with a call to
```

## Snippet 2

Context: `src/flamenco/runtime/fd_runtime.c:602` (changes a consensus- or validator-sensitive branch)

Before
```c
*/

  /* We want to cache the stake values for T-1 and T-2 in the forward
     looking vote states.  This is done as an optimization for tower
     calculations (T-1 stake) and clock calculation (T-2 stake).
     We use the current stake to populate the T-1 stake and the T-1
     stake to populate the T-2 stake. */
  fd_runtime_refresh_previous_stake_values( bank, runtime_stack );
```
After
```c
*/

  /* Now that our stakes caches have been updated, we can calculate the
     leader schedule for the upcoming epoch epoch using our new
```

## Snippet 3

Context: `src/flamenco/rewards/fd_rewards.c:467` (changes a consensus- or validator-sensitive branch)

Before
```c
uint idx = (uint)fd_vote_rewards_map_idx_query( vote_ele_map, &stake_delegation->vote_account, UINT_MAX, vote_ele );
    if( FD_UNLIKELY( idx==UINT_MAX ) ) continue;
    if( FD_UNLIKELY( vote_ele[idx].invalid ) ) continue;

    if( is_recalculation ) {
      /* We have not cached the stake points yet if we are recalculating
         stake rewards so we need to recalculate them. */
```
After
```c
uint idx = (uint)fd_vote_rewards_map_idx_query( vote_ele_map, &stake_delegation->vote_account, UINT_MAX, vote_ele );
    if( FD_UNLIKELY( idx==UINT_MAX ) ) continue;

    fd_calculated_stake_points_t   stake_points_result_[1];
    fd_calculated_stake_points_t * stake_points_result;
    if( is_recalculation || FD_UNLIKELY( stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) ) {
      /* We have not cached the stake points yet if we are recalculating
         stake rewards so we need to recalculate them. */
```

## Snippet 4

Context: `src/flamenco/rewards/fd_rewards.c:375` (changes a consensus- or validator-sensitive branch)

Before
```c
uint idx = (uint)fd_vote_rewards_map_idx_query( vote_ele_map, &stake_delegation->vote_account, UINT_MAX, vote_ele );
    FD_TEST( idx!=UINT_MAX );

    if( FD_UNLIKELY( vote_ele[idx].invalid ) ) continue;

    fd_calculated_stake_points_t * stake_point_result = &runtime_stack->stakes.stake_points_result[ stake_delegation->idx ];
    calculate_stake_points_and_credits( stake_history,
```
After
```c
uint idx = (uint)fd_vote_rewards_map_idx_query( vote_ele_map, &stake_delegation->vote_account, UINT_MAX, vote_ele );
    if( FD_UNLIKELY( idx==UINT_MAX ) ) continue;

    fd_calculated_stake_points_t   stake_points_result_[1];
    fd_calculated_stake_points_t * stake_points_result;
    if( FD_UNLIKELY( stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) ) {
      stake_points_result = stake_points_result_;
```

# Fix Pattern

Add an explicit capacity check before indexing a fixed-size runtime-stack cache, and provide a local per-iteration fallback for entries that cannot safely use the cache.

## How It Was Fixed

The patch declares a local `fd_calculated_stake_points_t stake_points_result_[1]` and routes out-of-capacity stake delegations to that local result. In-bounds delegations continue to use `runtime_stack->stakes.stake_points_result[ stake_delegation->idx ]`. The patch also makes missing vote-map entries non-fatal in the partitioned path by changing the assertion into a `continue`.

# Why It Matters

1. Reward calculation is consensus-sensitive state processing.

2. Fixed-cache capacity must not be treated as an implicit protocol maximum unless enforced elsewhere.

3. The patch prevents direct fixed-array indexing for out-of-capacity delegation indices.

4. The evidence supports likely hardening, not a confirmed exploit.

# Evidence Notes

Primary evidence comes from `src/flamenco/rewards/fd_rewards.c` around the supplied hunks at lines 375 and 467. The before code directly indexed `runtime_stack->stakes.stake_points_result[ stake_delegation->idx ]`; the after code checks `stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS` and uses a local fallback. Supporting context in `fd_runtime.c` and `fd_vote_stakes.h` shows related staking-cache and snapshot-loading work, but those snippets are mostly architectural context. The removed `vote_ele[idx].invalid` checks are not enough to claim an authorization or validation bypass. Protocol security invariant: Reward calculation must only index fixed-size runtime-stack stake-point caches when the stake delegation index is within the cache capacity; delegations outside that capacity must be handled without unsafe fixed-array access. Verification notes: The patch does not prove an externally exploitable attack path. The evidence does not prove a network-triggerable memory corruption primitive. The vote_ele invalid-check removal is not enough by itself to claim an authorization or validation bypass. The API/comment changes in fd_vote_stakes.h are not independently security fixes. The commit appears partly architectural decoupling, so classification should remain hardening/likely rather than confirmed vulnerability fix. No external exploit path is established by the supplied evidence. No network-triggerable memory corruption primitive is proven. The security classification rests on the before/after bounds check around a fixed-size cache in consensus-sensitive reward code. Helper or surrounding staking changes should be treated as support code unless further evidence shows they caused the unsafe index. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `bounds-check-hardening`
Final impact type: `memory-safety`
Final tags: `blockchain-core, staking, rewards, bounds-check, memory-safety, validator`

The supplied patch evidence supports retaining this as security hardening, but not as a confirmed consensus-safety vulnerability. The strongest evidence is that reward code previously indexed a fixed runtime-stack cache with stake_delegation->idx without a shown capacity guard, while the patch adds an explicit FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS check and a local fallback buffer. Because this is C code in validator reward processing, that is security-relevant memory-safety hardening, although the commit metadata and surrounding changes also indicate architectural decoupling and do not prove exploitability or an actual consensus failure.

## Security Evidence

1. Pre-patch calculate_reward_points_partitioned formed &runtime_stack->stakes.stake_points_result[ stake_delegation->idx ] without the supplied evidence showing a bounds check.
2. Post-patch code checks stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS and routes out-of-capacity entries to a local fd_calculated_stake_points_t buffer.
3. A related rewards path now recalculates stake points when the delegation index cannot safely use the fixed cache.
4. The changed code is in validator staking/reward calculation, a security-sensitive blockchain-core path.

## Missing Evidence

1. No supplied evidence proves an externally triggerable exploit path.
2. No supplied evidence proves actual memory corruption, crash, or consensus divergence occurred pre-patch.
3. The commit subject and body describe decoupling work rather than an explicit vulnerability fix.
4. The removed vote_ele invalid checks are not explained enough to support an authorization, validation-bypass, or consensus claim.

## Claim Boundaries

1. Validate as security-hardening, not a confirmed security-fix.
2. Do not claim a proven consensus failure from the supplied patch alone.
3. Do not claim network-triggerable memory corruption without additional evidence.
4. The fd_vote_stakes.h comment/API context and runtime epoch-cache changes are supporting context, not independently proven security fixes.
