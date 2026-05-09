---
case_id: case_20211206_e123883b26
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2021-12-06
source_refs:
  - git:e123883b2698070acac4543d2f372ede18a60ad7
  - "programs/vote/src/vote_state/mod.rs:898"
  - "programs/vote/src/vote_instruction.rs:409"
  - "programs/vote/src/vote_state/mod.rs:1903"
  - "programs/vote/src/vote_instruction.rs:509"
bug_class: missing-rent-exemption-check
tags:
  - infrastructure
  - consensus
  - rent-exemption
  - vote-account-lifecycle
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Solana vote-account withdrawal handling by adding feature-gated Rent sysvar plumbing and making the post-withdraw balance explicit. The provided evidence supports that the change is intended to reject withdrawals that would create non-rent-exempt vote accounts, but it does not establish unauthorized withdrawal, fund theft, lamport creation, or a concrete consensus failure.

## Observed Patch Facts

1. In `programs/vote/src/vote_state/mod.rs`, the patch replaces `match vote_account.lamports()?.cmp(&lamports) {` with `let remaining_balance = vote_account`.

2. In `programs/vote/src/vote_instruction.rs`, the patch replaces `vote_state::withdraw(me, lamports, to, &signers)` with `let rent_sysvar = if invoke_context`.

3. In `programs/vote/src/vote_state/mod.rs`, the patch replaces `// all good` with `None,`.

4. In `programs/vote/src/vote_instruction.rs`, the patch replaces `solana_program_runtime::invoke_context::mock_process_instruction(` with `let rent = Rent::default();`.

## Project Context

The changed code sits primarily in `programs/vote/src/vote_state`, `programs/vote/src`, `programs/vote`, which anchors the finding in the `consensus` area of the project. Historical context from `programs/vote/src/vote_transaction.rs`, `programs/vote/src/vote_state/vote_state_versions.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. The strongest project-level identifiers around this patch are `InstructionError::InsufficientFunds`, `lamports`, `sysvar::rent::id`, and `vote_account`.

## Before/After Behavior

Before the patch, `VoteInstruction::Withdraw` called `vote_state::withdraw` without Rent data, and the shown withdraw logic only rejected insufficient funds or deinitialized the vote account on an exact full-balance withdrawal. After the patch, the dispatcher fetches the Rent sysvar when `reject_non_rent_exempt_vote_withdraws` is active and passes optional Rent into `withdraw`; `withdraw` computes `remaining_balance` with `checked_sub` and preserves the zero-balance deinitialization path.

# Root Cause

The withdraw path did not have Rent context in the dispatcher call, so the shown implementation could not enforce a rent-exemption lifecycle check for partial withdrawals. The precise rejection branch is not included in the supplied excerpt, so the root cause should be limited to missing Rent-aware validation rather than broader state corruption or consensus failure.

## Walkthrough

1. An authorized vote-account withdrawal reaches `VoteInstruction::Withdraw(lamports)`.

2. Before the patch, the dispatcher passed the vote account, destination account, withdrawal amount, and signers to `vote_state::withdraw` without Rent data.

3. The shown old withdraw logic compared account lamports against the requested amount and rejected insufficient funds.

4. If the withdrawal fully drained the account, the old path deinitialized the vote account by writing a default vote state.

5. For partial withdrawals, the provided old-code evidence does not show a rent-exemption check.

6. After the patch, the dispatcher conditionally fetches `sysvar::rent::id()` when the feature gate is active.

7. The dispatcher passes `Some(rent)` or `None` into `vote_state::withdraw`.

8. The withdraw implementation computes `remaining_balance` explicitly with checked subtraction before deciding whether the account is fully drained or must satisfy the rent-related path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/vote/src/vote_state/mod.rs | 888 | withdraw implementation computes remaining vote-account balance and enforces the zero-balance versus rent-exempt lifecycle path |
| programs/vote/src/vote_instruction.rs | 409 | vote instruction dispatcher supplies Rent sysvar to Withdraw when the feature gate is active |
| programs/vote/src/vote_state/mod.rs | 1873 | unit tests cover insufficient funds and non-rent-exempt withdraw behavior before and after feature activation |
| programs/vote/src/vote_instruction.rs | 477 | instruction test harness adds Rent sysvar support for mocked vote instruction processing |

## Code Snippets

## Snippet 1

Context: `programs/vote/src/vote_state/mod.rs:898` (changes a consensus- or validator-sensitive branch)

Before
```rust
verify_authorized_signer(&vote_state.authorized_withdrawer, signers)?;

    match vote_account.lamports()?.cmp(&lamports) {
        Ordering::Less => return Err(InstructionError::InsufficientFunds),
        Ordering::Equal => {
            // Deinitialize upon zero-balance
            vote_account.set_state(&VoteStateVersions::new_current(VoteState::default()))?;
        }
```
After
```rust
verify_authorized_signer(&vote_state.authorized_withdrawer, signers)?;

    let remaining_balance = vote_account
        .lamports()?
        .checked_sub(lamports)
        .ok_or(InstructionError::InsufficientFunds)?;

    if remaining_balance == 0 {
```

## Snippet 2

Context: `programs/vote/src/vote_instruction.rs:409` (changes a consensus- or validator-sensitive branch)

Before
```rust
VoteInstruction::Withdraw(lamports) => {
            let to = keyed_account_at_index(keyed_accounts, first_instruction_account + 1)?;
            vote_state::withdraw(me, lamports, to, &signers)
        }
        VoteInstruction::AuthorizeChecked(vote_authorize) => {
```
After
```rust
VoteInstruction::Withdraw(lamports) => {
            let to = keyed_account_at_index(keyed_accounts, first_instruction_account + 1)?;
            let rent_sysvar = if invoke_context
                .feature_set
                .is_active(&feature_set::reject_non_rent_exempt_vote_withdraws::id())
            {
                Some(invoke_context.get_sysvar(&sysvar::rent::id())?)
            } else {
```

## Snippet 3

Context: `programs/vote/src/vote_state/mod.rs:1903` (changes a consensus- or validator-sensitive branch)

Before
```rust
),
            &signers,
        );
        assert_eq!(res, Err(InstructionError::InsufficientFunds));

        // all good
        let to_account = RefCell::new(AccountSharedData::default());
        let lamports = vote_account.borrow().lamports();
```
After
```rust
),
            &signers,
            None,
        );
        assert_eq!(res, Err(InstructionError::InsufficientFunds));

        // non rent exempt withdraw, before feature activation
        {
```

## Snippet 4

Context: `programs/vote/src/vote_instruction.rs:509` (changes persisted or aggregate state handling)

Before
```rust
.map(|(meta, account)| (meta.is_signer, meta.is_writable, meta.pubkey, account))
            .collect();
        solana_program_runtime::invoke_context::mock_process_instruction(
            &id(),
            Vec::new(),
            &instruction.data,
            &keyed_accounts,
            super::process_instruction,
```
After
```rust
.map(|(meta, account)| (meta.is_signer, meta.is_writable, meta.pubkey, account))
            .collect();

        let rent = Rent::default();
        let rent_sysvar = (sysvar::rent::id(), bincode::serialize(&rent).unwrap());
        solana_program_runtime::invoke_context::mock_process_instruction_with_sysvars(
            &id(),
            Vec::new(),
```

# Fix Pattern

Pass required sysvar context into the state-transition function and validate the post-withdraw account lifecycle state under a feature gate.

## How It Was Fixed

The patch extends the withdraw path to accept optional Rent data, obtains Rent from the invoke context when the feature is active, computes the remaining vote-account balance explicitly, and updates tests and mock instruction processing so Rent-aware withdraw behavior can be exercised.

# Why It Matters

1. Protects a vote-account lifecycle and rent-exemption invariant.

2. Prevents feature-active partial withdrawals from leaving initialized vote accounts under the rent-exempt threshold, as indicated by the commit subject and test comments.

3. Keeps zero-balance full-drain behavior separate from partial-withdraw behavior.

4. Does not prove signer bypass, theft, lamport creation, or direct consensus divergence.

# Evidence Notes

Strong evidence: commit subject says non-rent-exempt vote withdraws are rejected; `vote_instruction.rs` now fetches and passes Rent under `reject_non_rent_exempt_vote_withdraws`; `vote_state::withdraw` now accepts optional Rent and computes `remaining_balance`; tests mention non-rent-exempt withdraw behavior and add Rent sysvar support. Missing evidence: the supplied excerpt does not show the exact rent-threshold comparison or rejection error, so claims about the exact predicate and exploitability must remain bounded. Protocol security invariant: A vote-account withdrawal should not leave an initialized vote account in a non-rent-exempt state when the reject_non_rent_exempt_vote_withdraws feature is active; a full drain is handled separately by deinitializing the account at zero balance. Verification notes: Patch evidence does not show unauthorized withdrawal or signer bypass. Patch evidence does not prove fund theft or direct lamport creation. Patch evidence does not show consensus divergence by itself, only a consensus-sensitive vote-program state transition guard. Behavior before feature activation is intentionally preserved, so this is feature-gated hardening rather than an unconditional historical rejection. No broader vote transaction parsing or vote-state version migration issue is proven by the provided context. Supported as security hardening, not a confirmed exploitable vulnerability. Confidence is medium because the exact rent-exemption rejection branch is not shown in the provided snippets. No evidence supports broader state corruption, unauthorized access, fund theft, or consensus divergence claims. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-rent-exemption-check`
Final tags: `infrastructure, consensus, rent-exemption, vote-account-lifecycle, state-integrity`

The supplied evidence supports retaining this as security hardening: the commit is explicitly about rejecting vote-account withdrawals that would leave non-rent-exempt accounts, and the patch adds feature-gated Rent sysvar plumbing into a consensus-sensitive vote withdrawal path. The evidence does not prove a concrete exploit, unauthorized access, theft, lamport creation, or actual consensus divergence, so it should not be treated as a confirmed security fix or broad state-corruption case.

## Security Evidence

1. Commit subject states vote withdraws creating non-rent-exempt accounts are rejected.
2. Withdraw processing now fetches Rent sysvar under the reject_non_rent_exempt_vote_withdraws feature gate.
3. vote_state::withdraw now receives optional Rent context and explicitly computes remaining_balance before lifecycle handling.
4. Tests were updated to cover non-rent-exempt withdraw behavior before feature activation and mock Rent sysvar availability.

## Missing Evidence

1. The exact rent-threshold comparison and rejection branch are not shown in the supplied snippets.
2. No evidence shows unauthorized withdrawal, signer bypass, fund theft, or lamport creation.
3. No evidence shows an observed consensus failure or exploit scenario.

## Claim Boundaries

1. Classify as feature-gated security hardening, not a proven exploitable vulnerability.
2. Limit the bug class to missing rent-exemption validation for vote-account withdrawal lifecycle handling.
3. Do not claim broad state corruption or consensus divergence from the provided patch alone.
4. Behavior before feature activation appears intentionally preserved.
