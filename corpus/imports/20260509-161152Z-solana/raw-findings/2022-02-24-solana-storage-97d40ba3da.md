---
case_id: case_20220224_97d40ba3da
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2022-02-24
source_refs:
  - git:97d40ba3da7f70fb6f0f6e905f718c13820c09a4
  - "runtime/src/account_rent_state.rs:165"
  - "runtime/src/bank.rs:16981"
  - "sdk/src/system_transaction.rs:28"
  - "runtime/src/account_rent_state.rs:32"
bug_class: rent-state-validation-bypass
impact_type:
  - economic-integrity
  - state-integrity
tags:
  - blockchain-runtime
  - rent-validation
  - account-resize
  - state-invariant
  - economic-invariant
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a runtime rent-state validation bypass. The central supported change is in `runtime/src/account_rent_state.rs`, where `RentState::transition_allowed_from` now carries `do_support_realloc` and compares pre/post data sizes for `RentPaying(data_size)` accounts. This supports the commit subject that resized accounts must be rent exempt. The evidence does not support the heuristic claims about panics, malformed decoding, cryptographic logic, replay behavior, or direct privilege escalation.

## Observed Patch Facts

1. In `runtime/src/account_rent_state.rs`, the patch replaces `for post_rent_state in RentState::into_enum_iter() {` with `let post_rent_state = RentState::Uninitialized;`.

2. In `runtime/src/bank.rs`, the patch adds `#[derive(Serialize, Deserialize)]`.

3. In `sdk/src/system_transaction.rs`, the patch replaces `/// Create and sign new system_instruction::Assign transaction` with `/// Create and sign new SystemInstruction::Allocate transaction`.

4. In `runtime/src/account_rent_state.rs`, the patch replaces `pub(crate) fn transition_allowed_from(&self, pre_rent_state: &RentState) -> bool {` with `pub(crate) fn transition_allowed_from(`.

## Project Context

The changed code sits primarily in `runtime/src`, `sdk/src`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/accounts.rs`, `sdk/src/transport.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/accounts.rs`, `runtime/src/bank/transaction_account_state_info.rs`. The strongest project-level identifiers around this patch are `Self::RentPaying`, `RentState`, `RentPaying`, and `RentState::RentPaying`.

## Before/After Behavior

Before the patch, the shown transition rule rejected only cases where an account ended as `RentPaying` after starting from a non-`RentPaying` state. A pre-existing `RentPaying` account could remain `RentPaying` without the shown validator comparing the pre- and post-data sizes. After the patch, when realloc support is enabled and both pre/post states are `RentPaying`, the transition is allowed only if `post_data_size == pre_data_size`, with the inline rationale that a resized account cannot remain rent paying.

# Root Cause

The rent-state transition check treated `RentPaying` primarily as a category and did not enforce the `RentPaying(data_size)` component for accounts that were already rent paying. That left a validation gap for legacy rent-paying accounts whose data length changed during transaction execution.

## Walkthrough

1. `RentState::from_account` classifies nonzero-lamport, non-rent-exempt accounts as `RentPaying(account.data().len())`.

2. The pre-patch `transition_allowed_from` rule only rejected transitions into `RentPaying` from a non-`RentPaying` pre-state.

3. Because the pre-patch rule did not compare data sizes, the provided code does not show rejection of an already rent-paying account that remained rent paying after resizing.

4. The patch adds `do_support_realloc` and inspects `Self::RentPaying(post_data_size)`.

5. When the pre-state is also `RentPaying(pre_data_size)` and realloc support is enabled, the patched logic requires equal pre/post data sizes.

6. The added realloc and allocate helpers appear to support tests for account resize scenarios; they are not themselves shown as root-cause code.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/account_rent_state.rs | 23 | Computes account rent state from lamports and data length, including RentPaying(data_size). |
| runtime/src/account_rent_state.rs | 32 | Enforces allowed pre/post rent-state transitions and newly rejects resized RentPaying accounts when realloc support is enabled. |
| runtime/src/bank/transaction_account_state_info.rs | 1 | Tracks per-transaction account rent state for post-execution validation through check_rent_state. |
| sdk/src/transaction/error.rs | 127 | Defines InvalidRentPayingAccount, the transaction error corresponding to leaving an account below rent-exempt minimum. |
| runtime/src/bank.rs | 16981 | Adds test scaffolding for mocked realloc instructions exercising the runtime rent-state path. |
| sdk/src/system_transaction.rs | 28 | Adds an allocate transaction helper used to construct account resize scenarios. |

## Code Snippets

## Snippet 1

Context: `runtime/src/account_rent_state.rs:165` (changes the branch that decides whether execution stops or continues)

Before
```rust
#[test]
    fn test_transition_allowed_from() {
        for post_rent_state in RentState::into_enum_iter() {
            for pre_rent_state in RentState::into_enum_iter() {
                if post_rent_state == RentState::RentPaying
                    && pre_rent_state != RentState::RentPaying
                {
                    assert!(!post_rent_state.transition_allowed_from(&pre_rent_state));
```
After
```rust
#[test]
    fn test_transition_allowed_from() {
        let post_rent_state = RentState::Uninitialized;
        assert!(post_rent_state.transition_allowed_from(&RentState::Uninitialized, true));
        assert!(post_rent_state.transition_allowed_from(&RentState::RentExempt, true));
        assert!(post_rent_state.transition_allowed_from(&RentState::RentPaying(0), true));

        let post_rent_state = RentState::RentExempt;
```

## Snippet 2

Context: `runtime/src/bank.rs:16981` (changes signature or replay validation logic)

Before
```rust
);
    }
}
```
After
```rust
);
    }

    #[derive(Serialize, Deserialize)]
    enum MockReallocInstruction {
        Realloc(usize, u64, Pubkey),
    }
```

## Snippet 3

Context: `sdk/src/system_transaction.rs:28` (changes signature or replay validation logic)

Before
```rust
}

/// Create and sign new system_instruction::Assign transaction
pub fn assign(from_keypair: &Keypair, recent_blockhash: Hash, program_id: &Pubkey) -> Transaction {
```
After
```rust
}

/// Create and sign new SystemInstruction::Allocate transaction
pub fn allocate(
    payer_keypair: &Keypair,
    account_keypair: &Keypair,
    recent_blockhash: Hash,
    space: u64,
```

## Snippet 4

Context: `runtime/src/account_rent_state.rs:32` (changes a sensitive control or state-update path)

Before
```rust
}

    pub(crate) fn transition_allowed_from(&self, pre_rent_state: &RentState) -> bool {
        // Only a legacy RentPaying account may end in the RentPaying state after message processing
        !(self == &Self::RentPaying && pre_rent_state != &Self::RentPaying)
    }
}
```
After
```rust
}

    pub(crate) fn transition_allowed_from(
        &self,
        pre_rent_state: &RentState,
        do_support_realloc: bool,
    ) -> bool {
        if let Self::RentPaying(post_data_size) = self {
```

# Fix Pattern

Preserve enough state for post-transaction validation to distinguish unchanged legacy rent-paying accounts from resized rent-paying accounts, and reject the resized-below-rent-exempt case.

## How It Was Fixed

`RentState::transition_allowed_from` was changed to accept `do_support_realloc` and compare `RentPaying` data sizes. Under realloc support, an account that remains `RentPaying` is allowed only when it was already `RentPaying` and its data size is unchanged. Tests and helper code were added around realloc and allocate scenarios.

# Why It Matters

1. Prevents resized accounts from remaining below the rent-exempt threshold under the shown validation rule.

2. Keeps the legacy rent-paying allowance limited to unchanged account sizes.

3. Changes runtime transaction validity behavior in an economic state-invariant path.

# Evidence Notes

The supplied evidence supports a rent-state invariant fix, not the heuristic baseline's panic or malformed-decoding theory. The full `check_rent_state` call chain is only partially shown, and no concrete exploit transaction, consensus failure, or network-level attack is proven. Confidence is downgraded from high to medium because the security impact is inferred from runtime rent validation and the commit subject rather than demonstrated end to end. Protocol security invariant: Accounts that finish transaction processing with allocated data must satisfy Solana rent-state rules. The provided patch evidence specifically supports the invariant that, when realloc support is enabled, a legacy RentPaying account may remain RentPaying only if its data size did not change; resized accounts must not be left below the rent-exempt threshold. Verification notes: No concrete exploit path is proven by the patch evidence alone. No crash, panic, or malformed-decoding issue is shown. No cryptographic, signature, or replay-sensitive logic is shown as fixed. No direct privilege escalation is demonstrated. Consensus impact is plausible because transaction validity changes, but a network split scenario is not proven. The exact full call chain of check_rent_state is only partially shown in the provided context. Supported by the changed `RentState::transition_allowed_from` signature and logic. Supported by `RentState::from_account` encoding data length into `RentPaying(data_size)`. Supported by the commit subject: `Resized accounts must be rent exempt`. Not supported: panic, malformed input decoding, cryptographic failure, replay issue, or direct privilege escalation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rent-state-validation-bypass`
Final impact type: `economic-integrity, state-integrity`
Final tags: `blockchain-runtime, rent-validation, account-resize, state-invariant, economic-invariant`

The supplied patch evidence supports a security-relevant tightening of Solana runtime rent-state validation: resized accounts that remain rent-paying are no longer allowed when realloc support is active. This is a protocol/economic state invariant fix or hardening, but the evidence does not prove a concrete exploit, liveness failure, privilege escalation, cryptographic issue, or replay bug. The original security-fix and liveness framing is too strong; security-hardening is the conservative corpus classification.

## Security Evidence

1. Commit subject states that resized accounts must be rent exempt.
2. RentState::from_account classifies non-rent-exempt accounts as RentPaying(data_size), preserving data length as part of validation state.
3. transition_allowed_from now receives do_support_realloc and compares pre/post RentPaying data sizes.
4. Patched logic allows a RentPaying account to remain RentPaying under realloc support only if its data size is unchanged.
5. Tests and helpers were added for realloc/allocate scenarios around the runtime rent-state path.

## Missing Evidence

1. No concrete exploit transaction is shown.
2. No demonstrated liveness failure is shown.
3. No consensus split or validator divergence scenario is proven.
4. No privilege escalation, signature, cryptographic, or replay-sensitive bug is supported by the supplied diff.
5. The full end-to-end check_rent_state call path is only partially evidenced.

## Claim Boundaries

1. Keep the claim to rent-state validation for resized accounts under realloc support.
2. Do not claim malformed decoding, panic safety, cryptographic validation, or replay protection.
3. Do not classify as liveness-failure based on the supplied evidence alone.
4. Treat bank.rs and sdk helper changes as test/scaffolding support, not primary root cause evidence.
5. The evidence supports protocol/economic invariant hardening more confidently than a proven exploitable security fix.
