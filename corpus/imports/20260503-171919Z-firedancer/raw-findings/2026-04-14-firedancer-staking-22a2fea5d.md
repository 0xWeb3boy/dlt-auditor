---
case_id: case_20260414_22a2fea5d
project: firedancer
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2026-04-14
source_refs:
  - git:22a2fea5d66e7dc7d4933c2c40bebfc2b78264ad
  - "src/flamenco/runtime/program/vote/fd_vote_state_versioned.c:733"
  - "src/flamenco/runtime/program/vote/fd_vote_state_versioned.h:183"
  - "src/flamenco/stakes/fd_stakes.c:476"
  - "src/flamenco/stakes/fd_stakes.c:735"
bug_class: missing-owner-check
impact_type:
  - state-integrity
confidence: medium
tags:
  - staking
  - vote-account-validation
  - missing-owner-check
  - consensus-sensitive
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an owner-aware vote-account validation helper and switches two staking refresh paths to use it. The code now rejects account metadata whose owner is not the vote program before treating the account as initialized vote state. This is security-relevant hardening of a consensus-sensitive path, but the supplied evidence does not establish attacker control or a concrete vulnerability impact, so it should not be treated as a confirmed security fix.

## Observed Patch Facts

1. In `src/flamenco/runtime/program/vote/fd_vote_state_versioned.c`, the patch adds `int`.

2. In `src/flamenco/runtime/program/vote/fd_vote_state_versioned.h`, the patch adds `/* same as fd_vsv_is_correct_size_and_initialized, but also checks that`.

3. In `src/flamenco/stakes/fd_stakes.c`, the patch replaces `} else if( FD_UNLIKELY( !fd_vsv_is_correct_size_and_initialized( vote_ro->meta ) ||` with `} else if( FD_UNLIKELY( !fd_vsv_is_correct_size_owner_and_init( vote_ro->meta ) ||`.

4. In `src/flamenco/stakes/fd_stakes.c`, the patch replaces `} else if( FD_UNLIKELY( !fd_vsv_is_correct_size_and_initialized( vote_ro->meta ) ) ) {` with `} else if( FD_UNLIKELY( !fd_vsv_is_correct_size_owner_and_init( vote_ro->meta ) ) ) {`.

## Project Context

The changed code sits primarily in `src/flamenco/runtime/program/vote`, `src/flamenco/runtime/program`, `src/flamenco/stakes`, which anchors the finding in the `staking` area of the project. Historical context from `src/flamenco/stakes/fd_top_votes.c`, `src/flamenco/stakes/fd_stakes.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/flamenco/stakes/fd_top_votes.c`, `src/flamenco/runtime/sysvar/fd_sysvar_clock.c`. The strongest project-level identifiers around this patch are `meta`, `vote_ro`, `fd_vsv_is_correct_size_and_initialized`, and `fd_vsv_is_correct_size_owner_and_init`. Nearby tests or test-like files include `src/flamenco/runtime/tests/test_accdb_svm.c`, `src/flamenco/runtime/tests/generated/metadata.pb.h`.

## Before/After Behavior

Before the patch, the VAT and non-VAT stake refresh paths used `fd_vsv_is_correct_size_and_initialized( vote_ro->meta )` before interpreting opened account data as vote-account state. The supplied evidence does not show that predicate checking `meta->owner`. After the patch, both paths call `fd_vsv_is_correct_size_owner_and_init()`, which first compares `meta->owner` with `fd_solana_vote_program_id.key` and returns failure on mismatch, then delegates to the existing size-and-initialization check.

# Root Cause

The stake refresh call sites relied on structural vote-state validation without also requiring that the account metadata owner be the vote program. The evidence supports a missing owner check, but not a proven exploit path or demonstrated consensus failure.

## Walkthrough

1. Stake refresh opens an account from `accdb` using `stake_accum->pubkey`.

2. Previously, the shown call sites accepted the account for further vote-account handling if `fd_vsv_is_correct_size_and_initialized()` passed.

3. The patch adds `fd_vsv_is_correct_size_owner_and_init()` in the vote state versioned module.

4. The new helper rejects metadata whose `owner` differs from `fd_solana_vote_program_id.key`.

5. If the owner matches, the helper applies the existing size-and-initialization validation.

6. Both VAT and non-VAT stake refresh paths now use the owner-aware helper.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/runtime/program/vote/fd_vote_state_versioned.c | 733 | implements vote account validation that now rejects accounts not owned by the vote program |
| src/flamenco/runtime/program/vote/fd_vote_state_versioned.h | 183 | declares stricter vote account validation helper including owner check |
| src/flamenco/stakes/fd_stakes.c | 476 | VAT stake refresh path now requires vote program ownership before accepting vote account data and BLS pubkey state |
| src/flamenco/stakes/fd_stakes.c | 735 | non-VAT stake refresh path now requires vote program ownership before treating a delegated account as an existing vote account |

## Code Snippets

## Snippet 1

Context: `src/flamenco/runtime/program/vote/fd_vote_state_versioned.c:733` (changes an authorization or privilege gate)

Before
```c
return 0;
}
```
After
```c
return 0;
}

int
fd_vsv_is_correct_size_owner_and_init( fd_account_meta_t const * meta ) {
  if( FD_UNLIKELY( memcmp( meta->owner, fd_solana_vote_program_id.key, sizeof(fd_pubkey_t) ) ) ) {
    return 0;
  }
```

## Snippet 2

Context: `src/flamenco/runtime/program/vote/fd_vote_state_versioned.h:183` (changes an authorization or privilege gate)

Before
```c
fd_vsv_is_correct_size_and_initialized( fd_account_meta_t const * meta );

FD_PROTOTYPES_END
```
After
```c
fd_vsv_is_correct_size_and_initialized( fd_account_meta_t const * meta );

/* same as fd_vsv_is_correct_size_and_initialized, but also checks that
   the owner is the vote program */
int
fd_vsv_is_correct_size_owner_and_init( fd_account_meta_t const * meta );

FD_PROTOTYPES_END
```

## Snippet 3

Context: `src/flamenco/stakes/fd_stakes.c:476` (changes a consensus- or validator-sensitive branch)

Before
```c
if( FD_UNLIKELY( !fd_accdb_open_ro( accdb, vote_ro, xid, &stake_accum->pubkey ) ) ) {
      continue;
    } else if( FD_UNLIKELY( !fd_vsv_is_correct_size_and_initialized( vote_ro->meta ) ||
                            !fd_vote_account_is_v4_with_bls_pubkey( fd_account_data( vote_ro->meta ), vote_ro->meta->dlen ) ) ) {
      fd_accdb_close_ro( accdb, vote_ro );
```
After
```c
if( FD_UNLIKELY( !fd_accdb_open_ro( accdb, vote_ro, xid, &stake_accum->pubkey ) ) ) {
      continue;
    } else if( FD_UNLIKELY( !fd_vsv_is_correct_size_owner_and_init( vote_ro->meta ) ||
                            !fd_vote_account_is_v4_with_bls_pubkey( fd_account_data( vote_ro->meta ), vote_ro->meta->dlen ) ) ) {
      fd_accdb_close_ro( accdb, vote_ro );
```

## Snippet 4

Context: `src/flamenco/stakes/fd_stakes.c:735` (changes a consensus- or validator-sensitive branch)

Before
```c
if( FD_UNLIKELY( !fd_accdb_open_ro( accdb, vote_ro, xid, &stake_accum->pubkey ) ) ) {
      exists_t_1 = 0;
    } else if( FD_UNLIKELY( !fd_vsv_is_correct_size_and_initialized( vote_ro->meta ) ) ) {
      exists_t_1 = 0;
      fd_accdb_close_ro( accdb, vote_ro );
```
After
```c
if( FD_UNLIKELY( !fd_accdb_open_ro( accdb, vote_ro, xid, &stake_accum->pubkey ) ) ) {
      exists_t_1 = 0;
    } else if( FD_UNLIKELY( !fd_vsv_is_correct_size_owner_and_init( vote_ro->meta ) ) ) {
      exists_t_1 = 0;
      fd_accdb_close_ro( accdb, vote_ro );
```

# Fix Pattern

Add a centralized validation helper that composes ownership validation with existing structural validation, then replace call sites that interpret vote-account state.

## How It Was Fixed

`fd_vsv_is_correct_size_owner_and_init()` was added and declared in the vote state versioned implementation/header. The staking refresh paths in `fd_stakes.c` were updated to call that helper instead of the prior size/init-only predicate.

# Why It Matters

1. Stake refresh logic uses vote-account data in a consensus-sensitive subsystem.

2. Ownership is a stronger account-type boundary than layout checks alone.

3. The patch reduces the chance that non-vote-program-owned accounts are interpreted as vote accounts.

4. The provided evidence does not prove exploitability, attacker reachability, or quantified impact.

# Evidence Notes

Evidence directly supports that an owner check was added at `src/flamenco/runtime/program/vote/fd_vote_state_versioned.c:733`, documented in `fd_vote_state_versioned.h:183`, and used in two staking refresh call sites at `src/flamenco/stakes/fd_stakes.c:476` and `src/flamenco/stakes/fd_stakes.c:735`. Evidence does not establish attacker control, transaction authorization behavior, consensus divergence, reward manipulation, or any concrete vulnerability outcome. Protocol security invariant: Accounts interpreted as vote accounts during stake refresh should be owned by the Solana vote program in addition to having the expected vote-state size and initialized layout. Verification notes: The patch does not prove that an attacker could create or control a malicious account reaching this path. The patch does not show whether incorrect acceptance would cause consensus divergence, reward manipulation, or only local accounting differences. The patch does not establish that size and initialization checks were otherwise insufficient for all malformed data cases. The evidence does not show changes to transaction-level authorization or vote program instruction processing. Confirmed by supplied diff snippets only; no external code inspection was performed. Downgraded from confirmed security-fix because the vulnerability thesis is not established by the provided evidence. Kept bug class as missing-owner-check because the new helper explicitly adds vote-program owner validation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-owner-check`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `staking, vote-account-validation, missing-owner-check, consensus-sensitive, security-hardening`

The supplied patch evidence clearly shows an owner check being added before stake refresh paths treat account data as initialized vote state. Because vote-account ownership is a security-sensitive account-type boundary in staking/validator logic, this is supported as security hardening. The evidence does not prove attacker reachability, exploitability, or a concrete consensus/reward impact, so it should not be elevated to a confirmed security fix.

## Security Evidence

1. A new helper rejects accounts whose meta->owner does not match the Solana vote program id.
2. The helper then delegates to the existing size-and-initialization vote-state validation.
3. Both VAT and non-VAT stake refresh paths now use the owner-aware helper instead of size/init-only validation.
4. The changed call sites are in staking refresh logic, a consensus-sensitive validator path.

## Missing Evidence

1. No evidence shows that an attacker can create or route a non-vote-owned account into these paths.
2. No regression test or exploit scenario is supplied demonstrating the bad pre-patch behavior.
3. No evidence establishes concrete impact such as consensus divergence, reward manipulation, or state corruption.
4. No commit body or advisory text confirms this was fixing a known vulnerability.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. The supported bug class is a missing owner check, not proven state corruption.
3. Impact should be limited to conservative state-integrity or consensus-sensitive validation risk.
4. Do not claim exploitability, attacker control, or quantified protocol impact from the supplied evidence alone.
