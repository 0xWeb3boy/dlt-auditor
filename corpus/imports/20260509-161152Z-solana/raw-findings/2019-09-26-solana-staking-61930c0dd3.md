---
case_id: case_20190926_61930c0dd3
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
source_quality: high
date: 2019-09-26
source_refs:
  - git:61930c0dd3fac9924fe3f5e1c0d1d3491b9db10b
  - "programs/vote_api/src/vote_state.rs:385"
  - "programs/vote_api/src/vote_state.rs:429"
  - "programs/stake_api/src/stake_state.rs:44"
  - "programs/stake_api/src/stake_state.rs:410"
bug_class: authorization-check-hardening
impact_type:
  - unauthorized-sensitive-operation
confidence: medium
tags:
  - staking
  - vote-program
  - authorization
  - signature-verification
  - authority-model
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely authorization fix in Solana vote/stake authority handling. The strongest supported change is in vote withdrawal: the pre-patch path only required the vote account itself to be a signer, while the patched path loads VoteState and verifies vote_state.authorized_withdrawer against the vote account and other signers. Vote processing is also moved to shared verification of vote_state.authorized_voter. The stake changes appear to support a broader role-based authority model, but the provided hunks do not prove a standalone stake vulnerability.

## Observed Patch Facts

1. In `programs/vote_api/src/vote_state.rs`, the patch replaces `if vote_account.signer_key().is_none() {` with `other_signers: &[KeyedAccount],`.

2. In `programs/vote_api/src/vote_state.rs`, the patch replaces `if vote_state.authorized_voter_pubkey == Pubkey::default() {` with `if vote_state.authorized_voter == Pubkey::default() {`.

3. In `programs/stake_api/src/stake_state.rs`, the patch replaces `StakeState::Stake(stake) => Some(stake.clone()),` with `pub fn authorized_from(account: &Account) -> Option<Authorized> {`.

4. In `programs/stake_api/src/stake_state.rs`, the patch replaces `impl Lockup {` with `pub trait StakeAccount {`.

## Project Context

The changed code sits primarily in `programs/vote_api/src`, `programs/vote_api`, `programs/stake_api/src`, which anchors the finding in the `staking` area of the project. Historical context from `programs/vote_api/src/vote_instruction.rs`, `programs/stake_api/src/stake_instruction.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/vote_api/src/vote_instruction.rs`, `programs/stake_api/src/stake_instruction.rs`. The strongest project-level identifiers around this patch are `vote_state`, `authorized`, `vote_account`, and `Pubkey::default`.

## Before/After Behavior

Before the patch, vote withdrawal rejected only calls where vote_account.signer_key() was absent, tying the observed gate to the vote account signer. After the patch, withdraw accepts other_signers, loads VoteState, and calls verify_authorized_signer for vote_state.authorized_withdrawer. Before the patch, process_vote manually checked authorized_voter_pubkey against the vote account signer and other signers. After the patch, it checks vote_state.authorized_voter and delegates signer validation to verify_authorized_signer. StakeState::Stake is changed to carry Authorized and Lockup data with helper accessors, but the evidence mainly shows supporting state/API changes.

# Root Cause

The grounded root cause is an incomplete authority check in sensitive vote-program paths, especially withdrawal: authorization was tied to the vote account signer instead of the role-specific authority stored in account state. Broader stake-state changes support explicit authority roles but are not established as the root cause by the provided evidence.

## Walkthrough

1. A vote withdrawal entered withdraw with a vote account, lamport amount, and destination account.

2. In the pre-patch code, the shown guard only checked whether the vote account had a signer key.

3. The patched code deserializes VoteState from the vote account.

4. The patched code verifies the signer against vote_state.authorized_withdrawer, considering both the vote account and other_signers.

5. Vote processing similarly moves from manual comparison against an older authorized_voter_pubkey field to shared verification against vote_state.authorized_voter.

6. Stake state is reshaped to carry and expose Authorized role data, which supports the same role-based authority model but is not independently proven vulnerable here.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/vote_api/src/vote_state.rs | 385 | withdraw authorization now checks VoteState.authorized_withdrawer via verify_authorized_signer instead of only requiring vote_account signer |
| programs/vote_api/src/vote_state.rs | 422 | vote processing checks VoteState.authorized_voter through shared authorized-signer validation |
| programs/stake_api/src/stake_state.rs | 42 | stake state now carries and exposes Authorized role data alongside stake data |
| programs/stake_api/src/stake_state.rs | 407 | stake account initialization/authorization interface updated to accept Authorized and Lockup state |

## Code Snippets

## Snippet 1

Context: `programs/vote_api/src/vote_state.rs:385` (changes a consensus- or validator-sensitive branch)

Before
```rust
pub fn withdraw(
    vote_account: &mut KeyedAccount,
    lamports: u64,
    to_account: &mut KeyedAccount,
) -> Result<(), InstructionError> {
    if vote_account.signer_key().is_none() {
        return Err(InstructionError::MissingRequiredSignature);
    }
```
After
```rust
pub fn withdraw(
    vote_account: &mut KeyedAccount,
    other_signers: &[KeyedAccount],
    lamports: u64,
    to_account: &mut KeyedAccount,
) -> Result<(), InstructionError> {
    let vote_state: VoteState = vote_account.state()?;
```

## Snippet 2

Context: `programs/vote_api/src/vote_state.rs:429` (changes a consensus- or validator-sensitive branch)

Before
```rust
let mut vote_state: VoteState = vote_account.state()?;

    if vote_state.authorized_voter_pubkey == Pubkey::default() {
        return Err(InstructionError::UninitializedAccount);
    }

    let authorized = Some(&vote_state.authorized_voter_pubkey);
    // find a signer that matches the authorized_voter_pubkey
```
After
```rust
let mut vote_state: VoteState = vote_account.state()?;

    if vote_state.authorized_voter == Pubkey::default() {
        return Err(InstructionError::UninitializedAccount);
    }

    verify_authorized_signer(&vote_state.authorized_voter, vote_account, other_signers)?;
```

## Snippet 3

Context: `programs/stake_api/src/stake_state.rs:44` (changes persisted or aggregate state handling)

Before
```rust
}

    pub fn stake(&self) -> Option<Stake> {
        match self {
            StakeState::Stake(stake) => Some(stake.clone()),
            _ => None,
        }
```
After
```rust
}

    pub fn authorized_from(account: &Account) -> Option<Authorized> {
        Self::from(account).and_then(|state: Self| state.authorized())
    }

    pub fn stake(&self) -> Option<Stake> {
        match self {
```

## Snippet 4

Context: `programs/stake_api/src/stake_state.rs:410` (changes a sensitive control or state-update path)

Before
```rust
}

impl Lockup {
    fn check_authorized(
        &self,
        stake_pubkey_signer: Option<&Pubkey>,
        other_signers: &[KeyedAccount],
    ) -> Result<(), InstructionError> {
```
After
```rust
}

pub trait StakeAccount {
    fn initialize(
        &mut self,
        authorized: &Authorized,
        lockup: &Lockup,
    ) -> Result<(), InstructionError>;
```

# Fix Pattern

Replace account-key or field-specific signer checks with validation against role-specific authority stored in account state, and thread additional signer accounts through the affected instruction paths.

## How It Was Fixed

The vote program was changed so withdrawal and vote processing load VoteState and call verify_authorized_signer for authorized_withdrawer or authorized_voter. The stake program was changed so stake state can carry Authorized and Lockup data and expose authorized authority accessors.

# Why It Matters

1. Prevents vote withdrawal authorization from depending only on the vote account signer.

2. Separates sensitive vote roles such as voter and withdrawer.

3. Centralizes signer validation in shared authorized-signer logic.

4. Keeps stake state aligned with explicit stored authority roles.

# Evidence Notes

The strongest evidence is the withdraw hunk in programs/vote_api/src/vote_state.rs, where the authorization condition changes from requiring a vote account signer to checking vote_state.authorized_withdrawer. The process_vote hunk supports the same authority-check direction. The provided evidence does not prove arbitrary fund theft, vote forgery, consensus failure, or an end-to-end exploit. Stake changes may include API or serialization migration and should be treated as supporting context, not a proven standalone vulnerability. Protocol security invariant: Vote and stake operations should require signatures from the role-specific authority recorded in account state, such as the authorized voter or authorized withdrawer, rather than accepting only the vote account signer or ad hoc older authority fields. Verification notes: The patch does not prove arbitrary vote-account fund theft was exploitable. The patch does not prove consensus failure or validator vote forgery in isolation. The stake-state changes may partly be serialization/API migration rather than a standalone vulnerability fix. No concrete attacker preconditions or end-to-end exploit path are shown in the provided evidence. Do not classify this as state corruption based on the provided hunks; the clearest invariant is authorization. Confirmed from provided hunks that withdraw now verifies authorized_withdrawer. Confirmed from provided hunks that process_vote now verifies authorized_voter through shared logic. No provided test output or exploit scenario establishes concrete attacker preconditions. Stake authority changes are security-relevant context but not independently proven as the vulnerable path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-check-hardening`
Final impact type: `unauthorized-sensitive-operation`
Final confidence: `medium`
Final tags: `staking, vote-program, authorization, signature-verification, authority-model`

The provided hunks support retaining this as security hardening, not a proven security fix. The strongest evidence is that vote withdrawal changed from requiring only the vote account signer to verifying the stored role-specific authorized_withdrawer, and vote processing now uses shared verification of authorized_voter. That is clearly access-control-sensitive, but the patch evidence does not prove an exploitable pre-patch bypass, arbitrary fund theft, vote forgery, consensus failure, or state corruption.

## Security Evidence

1. Vote withdrawal now loads VoteState and verifies vote_state.authorized_withdrawer.
2. Pre-patch withdrawal evidence only shows a generic vote_account signer requirement.
3. Vote processing now verifies vote_state.authorized_voter through shared authorized-signer logic.
4. The changed code is in vote/stake authority handling, a security-sensitive subsystem.

## Missing Evidence

1. No exploit scenario or attacker preconditions are shown.
2. No test evidence demonstrates unauthorized withdrawal or unauthorized voting before the patch.
3. Stake changes appear to support an authority model but do not prove a standalone vulnerability.
4. The commit message frames the work as adding authorized parameters, not explicitly fixing a vulnerability.

## Claim Boundaries

1. Do not classify this as state corruption from the supplied evidence.
2. Do not claim arbitrary vote-account fund theft is proven.
3. Do not claim consensus failure or validator vote forgery is proven.
4. The validated finding is limited to authority-check hardening in vote/stake handling.
