---
case_id: case_20201116_e12cb457fb
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
impact_type:
  - state-integrity
source_quality: high
date: 2020-11-16
source_refs:
  - git:e12cb457fb0eae15e815da4c116a01ddcca671e1
  - "programs/stake/src/stake_state.rs:821"
  - "programs/stake/src/stake_state.rs:886"
  - "programs/stake/src/stake_state.rs:989"
  - "programs/stake/src/stake_instruction.rs:555"
bug_class: account-owner-validation
confidence: medium
tags:
  - staking
  - account-owner-validation
  - owner-check
  - incorrect-program-id
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit owner checks to Solana stake-management paths so delegate, split, and merge reject wrong-owner stake or vote account inputs with `InstructionError::IncorrectProgramId`. The commit subject and runtime guard changes support classifying this as an account-owner-validation security fix.

## Observed Patch Facts

1. In `programs/stake/src/stake_state.rs`, the patch adds `if vote_account.owner()? != solana_vote_program::id() {`.

2. In `programs/stake/src/stake_state.rs`, the patch adds `if split.owner()? != id() {`.

3. In `programs/stake/src/stake_state.rs`, the patch adds `if source_stake.owner()? != id() {`.

4. In `programs/stake/src/stake_instruction.rs`, the patch replaces `} else {` with `} else if meta.pubkey == invalid_stake_state_pubkey() {`.

## Project Context

The changed code sits primarily in `programs/stake/src`, `programs/stake`, which anchors the finding in the `staking` area of the project. Historical context from `programs/stake/src/legacy_stake_state.rs`, `programs/stake/src/legacy_stake_processor.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/stake/src/legacy_stake_state.rs`, `programs/stake/src/legacy_stake_processor.rs`. The strongest project-level identifiers around this patch are `InstructionError::IncorrectProgramId`, `Account::default`, `InstructionError`, and `meta`.

## Before/After Behavior

Before the patch, the shown delegate, split, and merge paths proceeded to inspect account state without the newly added owner checks on the role-bearing input accounts. After the patch, delegate rejects vote accounts not owned by `solana_vote_program::id()`, while split and merge reject stake-account inputs not owned by the stake program `id()`. Test setup was adjusted so invalid-state stake and vote test accounts have the expected owners, keeping invalid-state coverage separate from wrong-owner rejection.

# Root Cause

Stake-management code lacked explicit owner validation for some account parameters before interpreting them according to stake or vote account roles.

## Walkthrough

1. `delegate` receives a `vote_account` input for stake delegation.

2. Pre-patch evidence shows the path entering `match self.state()?` without the added vote-account owner check.

3. The patched path returns `InstructionError::IncorrectProgramId` unless `vote_account.owner()? == solana_vote_program::id()`.

4. `split` receives a destination split account.

5. Pre-patch evidence shows the path checking `split.state()?` without the added stake-program owner check.

6. The patched path returns `InstructionError::IncorrectProgramId` unless `split.owner()? == id()`.

7. `merge` receives a `source_stake` account.

8. Pre-patch evidence shows the path continuing toward state handling without the added source owner check.

9. The patched path returns `InstructionError::IncorrectProgramId` unless `source_stake.owner()? == id()`.

10. The test helper changes create invalid stake and vote state accounts under the expected owner programs, supporting tests for invalid state after wrong-owner inputs are rejected.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/stake/src/stake_state.rs | 821 | delegate rejects vote_account unless owned by solana_vote_program |
| programs/stake/src/stake_state.rs | 886 | split rejects split account unless owned by stake program |
| programs/stake/src/stake_state.rs | 989 | merge rejects source_stake account unless owned by stake program |
| programs/stake/src/stake_instruction.rs | 555 | test account construction updated to model invalid stake/vote state under the expected owner programs |

## Code Snippets

## Snippet 1

Context: `programs/stake/src/stake_state.rs:821` (changes an authorization or privilege gate)

Before
```rust
signers: &HashSet<Pubkey>,
    ) -> Result<(), InstructionError> {
        match self.state()? {
            StakeState::Initialized(meta) => {
```
After
```rust
signers: &HashSet<Pubkey>,
    ) -> Result<(), InstructionError> {
        if vote_account.owner()? != solana_vote_program::id() {
            return Err(InstructionError::IncorrectProgramId);
        }

        match self.state()? {
            StakeState::Initialized(meta) => {
```

## Snippet 2

Context: `programs/stake/src/stake_state.rs:886` (changes an authorization or privilege gate)

Before
```rust
signers: &HashSet<Pubkey>,
    ) -> Result<(), InstructionError> {
        if let StakeState::Uninitialized = split.state()? {
            // verify enough account lamports
```
After
```rust
signers: &HashSet<Pubkey>,
    ) -> Result<(), InstructionError> {
        if split.owner()? != id() {
            return Err(InstructionError::IncorrectProgramId);
        }

        if let StakeState::Uninitialized = split.state()? {
            // verify enough account lamports
```

## Snippet 3

Context: `programs/stake/src/stake_state.rs:989` (changes an authorization or privilege gate)

Before
```rust
signers: &HashSet<Pubkey>,
    ) -> Result<(), InstructionError> {
        let meta = match self.state()? {
            StakeState::Stake(meta, stake) => {
```
After
```rust
signers: &HashSet<Pubkey>,
    ) -> Result<(), InstructionError> {
        if source_stake.owner()? != id() {
            return Err(InstructionError::IncorrectProgramId);
        }

        let meta = match self.state()? {
            StakeState::Stake(meta, stake) => {
```

## Snippet 4

Context: `programs/stake/src/stake_instruction.rs:555` (changes an authorization or privilege gate)

Before
```rust
} else if sysvar::rent::check_id(&meta.pubkey) {
                    sysvar::rent::create_account(1, &Rent::default())
                } else {
                    Account::default()
```
After
```rust
} else if sysvar::rent::check_id(&meta.pubkey) {
                    sysvar::rent::create_account(1, &Rent::default())
                } else if meta.pubkey == invalid_stake_state_pubkey() {
                    let mut account = Account::default();
                    account.owner = id();
                    account
                } else if meta.pubkey == invalid_vote_state_pubkey() {
                    let mut account = Account::default();
```

# Fix Pattern

Validate account owner program at the instruction boundary before interpreting account state or continuing stake-management logic.

## How It Was Fixed

The patch added owner checks in `programs/stake/src/stake_state.rs` for delegate, split, and merge. It also updated test account construction in `programs/stake/src/stake_instruction.rs` so special invalid stake and vote accounts are owned by the expected programs.

# Why It Matters

1. Prevents wrong-owner accounts from being treated as stake or vote accounts in these paths.

2. Enforces a core account ownership invariant for stake management.

3. Covers delegate, split, and merge operations.

4. Evidence does not establish economic impact, signature bypass, or consensus divergence.

# Evidence Notes

Primary evidence is commit `e12cb457fb0eae15e815da4c116a01ddcca671e1` with subject `Reject faked stake/vote accounts in stake mgmt. (bp #13615) (#13620)`. Runtime guards were added in `programs/stake/src/stake_state.rs` at the shown delegate, split, and merge hunks. The `programs/stake/src/stake_instruction.rs` change appears to be test support, not the root cause. Protocol security invariant: Stake-management instructions must only consume accounts whose owner program matches the account role: vote accounts used for delegation must be owned by the vote program, and stake accounts used for split or merge must be owned by the stake program. Verification notes: Patch evidence does not prove a complete exploit path or economic impact. Patch evidence does not show whether forged accounts could bypass signatures independently. Patch evidence does not establish consensus divergence by itself. Legacy processor context is related but the shown fix is in stake_state management paths. Supported by explicit owner-check additions returning `InstructionError::IncorrectProgramId`. Supported by commit text referring to faked stake/vote accounts. No provided evidence proves a complete exploit path or financial impact. No provided evidence proves consensus divergence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `account-owner-validation`
Final confidence: `medium`
Final tags: `staking, account-owner-validation, owner-check, incorrect-program-id`

The supplied patch clearly adds runtime owner-program validation for stake-management account parameters before those accounts are interpreted as vote or stake accounts, and the commit explicitly describes rejecting faked stake/vote accounts. That supports retaining the case as security hardening in a security-sensitive staking subsystem. However, the evidence does not prove a concrete exploit path, state corruption outcome, economic loss, or consensus impact, so classifying it as a confirmed security fix for state corruption is too strong.

## Security Evidence

1. Adds a vote account owner check requiring `solana_vote_program::id()` before delegation logic proceeds.
2. Adds stake program owner checks for split and merge account inputs before state handling proceeds.
3. Wrong-owner inputs now fail with `InstructionError::IncorrectProgramId`.
4. Commit subject explicitly says the change rejects faked stake/vote accounts in stake management.

## Missing Evidence

1. No supplied evidence shows an exploit path using wrong-owner accounts.
2. No supplied evidence proves state corruption, fund loss, signature bypass, or consensus divergence.
3. No test output or vulnerability advisory is provided tying the bug to a concrete security incident.

## Claim Boundaries

1. Supported claim: stake management now rejects wrong-owner stake or vote account inputs.
2. Supported claim: this tightens account ownership invariants in a security-sensitive subsystem.
3. Unsupported claim: the patch proves an exploitable state-corruption vulnerability.
4. Unsupported claim: the patch proves economic or consensus impact.
