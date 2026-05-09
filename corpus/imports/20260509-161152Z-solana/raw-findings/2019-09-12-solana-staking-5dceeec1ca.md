---
case_id: case_20190912_5dceeec1ca
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: medium
date: 2019-09-12
source_refs:
  - git:5dceeec1ca0769726ef2fd89286111da2401aaa7
  - "programs/stake_api/src/stake_state.rs:472"
  - "programs/stake_api/src/stake_state.rs:503"
  - "programs/stake_api/src/stake_state.rs:597"
  - "programs/stake_api/src/stake_state.rs:564"
bug_class: improper-authorization
impact_type:
  - unauthorized-staking-operation
  - unauthorized-funds-movement
confidence: medium
tags:
  - staking
  - authorization
  - access-control
  - signature-check
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes staking control paths to use `stake.check_authorized(...)` and `lockup.check_authorized(...)` with `other_signers`, but the supplied evidence does not establish that the previous behavior was an exploitable vulnerability. The commit also appears to add or generalize authorized-staker functionality, so this is best treated as potentially security-relevant authorization work rather than a confirmed vulnerability fix.

## Observed Patch Facts

1. In `programs/stake_api/src/stake_state.rs`, the patch replaces `if self.signer_key().is_none() {` with `other_signers: &[KeyedAccount],`.

2. In `programs/stake_api/src/stake_state.rs`, the patch replaces `if self.signer_key().is_none() {` with `other_signers: &[KeyedAccount],`.

3. In `programs/stake_api/src/stake_state.rs`, the patch replaces `if lockup > clock.slot {` with `lockup.check_authorized(self.signer_key(), other_signers)?;`.

4. In `programs/stake_api/src/stake_state.rs`, the patch replaces `if self.signer_key().is_none() {` with `other_signers: &[KeyedAccount],`.

## Project Context

The changed code sits primarily in `programs/stake_api/src`, `programs/stake_api`, which anchors the finding in the `staking` area of the project. Historical context from `programs/stake_api/src/stake_instruction.rs`, `programs/stake_api/src/config.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/stake_api/src/stake_instruction.rs`, `programs/stake_api/src/config.rs`. The strongest project-level identifiers around this patch are `InstructionError::MissingRequiredSignature`, `sysvar::clock::Clock`, `clock`, and `InstructionError`.

## Before/After Behavior

Before the change, the shown `delegate_stake`, `deactivate_stake`, and `withdraw` paths checked whether `self.signer_key()` was present before continuing. After the change, these paths accept `other_signers` and call state-specific authorization helpers before creating stake state, deactivating stake, or allowing withdrawal logic to continue. The lockup withdrawal condition is also expressed as `lockup.slot > clock.slot`.

# Root Cause

The evidence supports only that authorization logic was redesigned from a signer-presence check to state-specific authorization checks. It does not prove that the earlier signer check accepted an unauthorized party, nor does it include enough surrounding account semantics or `check_authorized` implementation to establish a concrete root-cause vulnerability.

## Walkthrough

1. `delegate_stake` previously rejected missing `self.signer_key()` and now calls `lockup.check_authorized(self.signer_key(), other_signers)?` before constructing delegated stake state.

2. `deactivate_stake` previously rejected missing `self.signer_key()` and now calls `stake.check_authorized(self.signer_key(), other_signers)?` before deactivating stake.

3. `withdraw` now accepts `other_signers` so downstream stake or lockup branches can evaluate additional signer context.

4. In the stake withdrawal branch, the patch calls `stake.check_authorized(...)` before applying stake-balance withdrawal constraints.

5. In the lockup withdrawal branch, the patch calls `lockup.check_authorized(...)` before checking whether the lockup slot has expired.

6. The provided evidence does not show that a non-authority could previously delegate, deactivate, or withdraw funds.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/stake_api/src/stake_state.rs | 469 | delegate_stake now checks lockup authorization before creating delegated stake state |
| programs/stake_api/src/stake_state.rs | 501 | deactivate_stake now checks stake authorization before changing deactivation state |
| programs/stake_api/src/stake_state.rs | 560 | withdraw now accepts additional signer context for authorization checks |
| programs/stake_api/src/stake_state.rs | 568 | withdraw/transfer path checks stake or lockup authorization before permitting lamport movement |

## Code Snippets

## Snippet 1

Context: `programs/stake_api/src/stake_state.rs:472` (changes a sensitive control or state-update path)

Before
```rust
clock: &sysvar::clock::Clock,
        config: &Config,
    ) -> Result<(), InstructionError> {
        if self.signer_key().is_none() {
            return Err(InstructionError::MissingRequiredSignature);
        }

        if let StakeState::Lockup(lockup) = self.state()? {
```
After
```rust
clock: &sysvar::clock::Clock,
        config: &Config,
        other_signers: &[KeyedAccount],
    ) -> Result<(), InstructionError> {
        if let StakeState::Lockup(lockup) = self.state()? {
            lockup.check_authorized(self.signer_key(), other_signers)?;
            let stake = Stake::new(
                self.account.lamports,
```

## Snippet 2

Context: `programs/stake_api/src/stake_state.rs:503` (changes a sensitive control or state-update path)

Before
```rust
_vote_account: &KeyedAccount, // TODO: used in slashing
        clock: &sysvar::clock::Clock,
    ) -> Result<(), InstructionError> {
        if self.signer_key().is_none() {
            return Err(InstructionError::MissingRequiredSignature);
        }

        if let StakeState::Stake(mut stake) = self.state()? {
```
After
```rust
_vote_account: &KeyedAccount, // TODO: used in slashing
        clock: &sysvar::clock::Clock,
        other_signers: &[KeyedAccount],
    ) -> Result<(), InstructionError> {
        if let StakeState::Stake(mut stake) = self.state()? {
            stake.check_authorized(self.signer_key(), other_signers)?;
            stake.deactivate(clock.epoch);
```

## Snippet 3

Context: `programs/stake_api/src/stake_state.rs:597` (changes a sensitive control or state-update path)

Before
```rust
}
            StakeState::Lockup(lockup) => {
                if lockup > clock.slot {
                    return Err(InstructionError::InsufficientFunds);
                }
            }
            StakeState::Uninitialized => {}
            _ => return Err(InstructionError::InvalidAccountData),
```
After
```rust
}
            StakeState::Lockup(lockup) => {
                lockup.check_authorized(self.signer_key(), other_signers)?;
                if lockup.slot > clock.slot {
                    return Err(InstructionError::InsufficientFunds);
                }
            }
            StakeState::Uninitialized => {
```

## Snippet 4

Context: `programs/stake_api/src/stake_state.rs:564` (changes a sensitive control or state-update path)

Before
```rust
clock: &sysvar::clock::Clock,
        stake_history: &sysvar::stake_history::StakeHistory,
    ) -> Result<(), InstructionError> {
        if self.signer_key().is_none() {
            return Err(InstructionError::MissingRequiredSignature);
        }

        fn transfer(
```
After
```rust
clock: &sysvar::clock::Clock,
        stake_history: &sysvar::stake_history::StakeHistory,
        other_signers: &[KeyedAccount],
    ) -> Result<(), InstructionError> {
        fn transfer(
            from: &mut Account,
```

# Fix Pattern

Replace signer-presence checks with explicit state-derived authorization checks and thread additional signer context through the affected staking methods.

## How It Was Fixed

The patch added `other_signers: &[KeyedAccount]` parameters and inserted `stake.check_authorized(...)` or `lockup.check_authorized(...)` calls in sensitive staking paths. It also retained a missing-signature check for the uninitialized withdrawal branch and clarified the lockup slot comparison.

# Why It Matters

1. Stake delegation and deactivation are authority-sensitive operations.

2. Withdrawals move lamports and require clear authorization boundaries.

3. The change may reduce authorization ambiguity.

4. Exploitability is not established from the supplied evidence.

# Evidence Notes

Grounded evidence is limited to hunks in `programs/stake_api/src/stake_state.rs` showing replacement of `self.signer_key().is_none()` checks with `check_authorized(...)` calls. The evidence does not include `check_authorized`, full instruction-account validation, prior account signer semantics, or tests proving an unauthorized action was possible. Claims of fund theft, consensus failure, validator compromise, or confirmed vulnerability are unsupported. Protocol security invariant: Stake account operations that change staking state or move lamports should be authorized by the authority defined in the stake or lockup state, not merely by whatever signature condition the account-processing path happens to expose. Verification notes: The patch does not prove funds could be stolen before the change. The patch does not prove consensus failure or validator compromise. The patch does not show the full implementation of `check_authorized`. The commit may partly be new authorized-staker functionality rather than a vulnerability fix. The exact privilege relation between `self.signer_key()` and the authorized pubkey is inferred from the provided hunks only. Downgraded from likely security-hardening to unclear because the vulnerability thesis is not proven. Downgraded confidence to low due to missing authorization helper and account signer semantics. Set `keep_in_security_corpus` to false under the rule for unclear security relevance. Preserved `improper-authorization` only as a tentative bug class because the patch touches authorization checks. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-authorization`
Final impact type: `unauthorized-staking-operation, unauthorized-funds-movement`
Final confidence: `medium`
Final tags: `staking, authorization, access-control, signature-check, security-hardening`

The supplied patch evidence supports keeping this as security hardening, not as a confirmed vulnerability fix. Multiple staking operations that delegate stake, deactivate stake, or withdraw lamports change from a generic signer-presence check to state-specific `stake.check_authorized(...)` or `lockup.check_authorized(...)` checks with additional signer context. That is a clear tightening of authorization behavior in security-sensitive staking and withdrawal paths, although the evidence does not prove that exploitation was previously possible.

## Security Evidence

1. Sensitive staking operations changed from `self.signer_key().is_none()` checks to explicit state-derived authorization checks.
2. `delegate_stake` now calls `lockup.check_authorized(...)` before creating delegated stake state.
3. `deactivate_stake` now calls `stake.check_authorized(...)` before deactivating stake.
4. `withdraw` now threads `other_signers` and checks stake or lockup authorization before allowing withdrawal-path logic to proceed.
5. The affected code controls stake state transitions and lamport transfers.

## Missing Evidence

1. No implementation of `check_authorized` is provided.
2. No full pre-patch account signer semantics are provided.
3. No test or exploit scenario shows that an unauthorized signer could previously delegate, deactivate, or withdraw.
4. The commit message frames this partly as adding authorized-staker functionality, which may be product/security-model work rather than a vulnerability fix.

## Claim Boundaries

1. Validate only as security hardening, not a confirmed security fix.
2. Do not claim proven fund theft or confirmed authorization bypass from the supplied evidence alone.
3. Do not claim consensus failure, validator compromise, or state corruption.
4. The supported claim is that authorization checks were made stricter and more state-specific in sensitive staking paths.
