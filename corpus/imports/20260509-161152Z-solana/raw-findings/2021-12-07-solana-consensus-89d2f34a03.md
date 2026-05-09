---
case_id: case_20211207_89d2f34a03
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2021-12-07
source_refs:
  - git:89d2f34a038318bbe36d2eb49d6c4b0e1d4adac8
  - "programs/vote/src/vote_state/mod.rs:898"
  - "programs/vote/src/vote_instruction.rs:409"
  - "programs/vote/src/vote_state/mod.rs:1903"
  - "programs/vote/src/vote_instruction.rs:509"
bug_class: protocol-invariant-enforcement
impact_type:
  - state-integrity
tags:
  - infrastructure
  - consensus
  - rent-exemption
  - protocol-invariant
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to harden the Solana vote-program withdraw path by adding Rent context under the `reject_non_rent_exempt_vote_withdraws` feature and changing withdrawal handling around the remaining vote-account balance. The supplied evidence supports a rent-exemption invariant fix, but does not establish an exploit, theft, signer bypass, memory issue, or demonstrated consensus failure.

## Observed Patch Facts

1. In `programs/vote/src/vote_state/mod.rs`, the patch replaces `match vote_account.lamports()?.cmp(&lamports) {` with `let remaining_balance = vote_account`.

2. In `programs/vote/src/vote_instruction.rs`, the patch replaces `vote_state::withdraw(me, lamports, to, &signers)` with `let rent_sysvar = if invoke_context`.

3. In `programs/vote/src/vote_state/mod.rs`, the patch replaces `// all good` with `None,`.

4. In `programs/vote/src/vote_instruction.rs`, the patch replaces `solana_program_runtime::invoke_context::mock_process_instruction(` with `let rent = Rent::default();`.

## Project Context

The changed code sits primarily in `programs/vote/src/vote_state`, `programs/vote/src`, `programs/vote`, which anchors the finding in the `consensus` area of the project. Historical context from `programs/vote/src/vote_transaction.rs`, `programs/vote/src/vote_state/vote_state_versions.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. The strongest project-level identifiers around this patch are `InstructionError::InsufficientFunds`, `lamports`, `sysvar::rent::id`, and `vote_account`.

## Before/After Behavior

Before the patch, the vote withdraw path compared the vote-account lamports to the requested withdrawal amount and handled insufficient funds or exact full-drain deinitialization, with no supplied evidence of a Rent-backed check for partial withdrawals. The instruction dispatcher called `vote_state::withdraw` without loading Rent. After the patch, the dispatcher conditionally loads the Rent sysvar when `reject_non_rent_exempt_vote_withdraws` is active and passes it into `withdraw`; `withdraw` computes `remaining_balance` with checked subtraction and preserves the zero-balance deinitialization path. The provided snippets imply, but do not directly show, rejection of nonzero non-rent-exempt remainders.

# Root Cause

The withdraw path did not have Rent context on the activated instruction path, so a partial withdrawal could proceed without the supplied evidence showing enforcement that the remaining initialized vote account stayed rent-exempt.

## Walkthrough

1. The withdraw function reads the current vote state and verifies the authorized withdrawer signer.

2. The old code rejected insufficient funds and deinitialized the vote account on an exact full-balance withdrawal.

3. For partial withdrawals, the supplied before snippet does not show a Rent-backed remainder check.

4. The patched instruction dispatcher checks the `reject_non_rent_exempt_vote_withdraws` feature flag.

5. When the feature is active, the dispatcher loads `sysvar::rent::id()` and passes `Some(Rent)` to `vote_state::withdraw`; otherwise it passes `None`.

6. The patched withdraw logic computes `remaining_balance` with checked subtraction and keeps the full-drain deinitialization case.

7. Tests and mocks were updated to pass the new Rent option or supply the Rent sysvar.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/vote/src/vote_state/mod.rs | 888 | withdraw implementation computes remaining vote-account balance, deinitializes on full drain, and enforces the rent-exempt remainder invariant when rent data is supplied |
| programs/vote/src/vote_instruction.rs | 409 | vote instruction dispatcher loads the Rent sysvar when reject_non_rent_exempt_vote_withdraws is active and passes it into vote_state::withdraw |
| programs/vote/src/vote_state/mod.rs | 1873 | unit coverage exercises withdraw authorization, insufficient funds, and pre-feature non-rent-exempt behavior |
| programs/vote/src/vote_instruction.rs | 477 | instruction test harness supplies the Rent sysvar needed by the updated withdraw path |

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

Thread required sysvar context into the state-transition path under a feature gate, compute the post-withdrawal balance explicitly, and reject invalid partial-withdrawal results when Rent validation is available.

## How It Was Fixed

`vote_state::withdraw` was changed to accept optional Rent context and compute the remaining balance with checked subtraction. `vote_instruction::process_instruction` now supplies Rent only when the new feature is active, preserving pre-feature behavior with `None`. Tests and the mock instruction harness were adjusted for the new argument and sysvar dependency.

# Why It Matters

1. Maintains a vote-account rent-exemption invariant after partial withdrawals.

2. Keeps full-drain deinitialization behavior separate from partial-withdrawal behavior.

3. Feature gating limits behavior change to the activated protocol path.

4. Evidence does not prove direct asset theft or consensus divergence.

# Evidence Notes

Grounded evidence includes the commit subject, the feature name `reject_non_rent_exempt_vote_withdraws`, Rent sysvar loading in `programs/vote/src/vote_instruction.rs`, and remaining-balance computation in `programs/vote/src/vote_state/mod.rs`. The actual rejection condition for a nonzero non-rent-exempt remainder is not present in the supplied snippets, so claims depending on that exact code path are treated as inferred from commit context and mapper output rather than directly shown. Protocol security invariant: When the feature is active, a vote-account withdrawal should either fully drain and deinitialize the vote account or leave the still-initialized vote account rent-exempt. Verification notes: The patch does not prove arbitrary theft of lamports or bypass of the authorized withdrawer signer check. The evidence does not show a remote crash, memory-safety issue, or serialization vulnerability. The evidence does not establish that non-rent-exempt vote-account creation caused consensus divergence in practice. Behavior before feature activation is intentionally preserved, so the mapping is limited to the activated feature path. Do not claim authorized-withdrawer bypass; signer verification remains present. Do not claim arbitrary lamport theft, memory corruption, serialization failure, or observed consensus divergence. Confidence is downgraded because the provided snippets do not directly show the final rent-exemption rejection branch. Treat test harness changes as support code, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-invariant-enforcement`
Final impact type: `state-integrity`
Final tags: `infrastructure, consensus, rent-exemption, protocol-invariant, state-integrity`

The supplied evidence supports retaining this as security hardening, not a proven security fix. The commit and feature name explicitly reject vote withdrawals that would leave initialized vote accounts non-rent-exempt, and the patch threads Rent sysvar context into the vote withdraw path under a feature gate. That is a tightened invariant in a consensus-sensitive subsystem. However, the snippets do not directly show the final rejection branch or demonstrate exploitability, unauthorized access, theft, or observed consensus failure, so the original state-corruption framing is too strong.

## Security Evidence

1. Commit subject says vote withdraws creating non-rent-exempt accounts are rejected.
2. Vote withdraw processing conditionally loads the Rent sysvar when reject_non_rent_exempt_vote_withdraws is active.
3. withdraw now computes remaining_balance with checked subtraction before deciding full-drain versus partial-withdraw behavior.
4. Tests reference non-rent-exempt withdraw behavior before feature activation, supporting an intentional protocol behavior change.

## Missing Evidence

1. The supplied snippets do not show the exact code that rejects a nonzero non-rent-exempt remaining balance.
2. No exploit path, unauthorized withdrawal, or signer bypass is demonstrated.
3. No evidence shows actual consensus divergence, account corruption, or loss of funds in practice.

## Claim Boundaries

1. Treat as protocol hardening around rent-exemption invariants, not a confirmed exploit fix.
2. Do not claim arbitrary lamport theft or authorization bypass.
3. Do not claim memory corruption, serialization vulnerability, or demonstrated consensus failure.
4. Scope is limited to activated feature behavior for vote-account withdrawals.
