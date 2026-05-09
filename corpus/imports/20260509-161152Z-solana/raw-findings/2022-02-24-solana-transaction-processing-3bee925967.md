---
case_id: case_20220224_3bee925967
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2022-02-24
source_refs:
  - git:3bee9259672902cb47bf7f2f11e766b8ffee090b
  - "runtime/src/account_rent_state.rs:138"
  - "runtime/src/bank.rs:17284"
  - "sdk/src/system_transaction.rs:28"
  - "runtime/src/account_rent_state.rs:31"
bug_class: rent-resource-accounting-invariant
impact_type:
  - resource-accounting-invariant
tags:
  - infrastructure
  - transaction-processing
  - rent-validation
  - account-reallocation
  - resource-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a Solana runtime rent-validation invariant gap. The strongest evidence is the change to `RentState::transition_allowed_from`, which adds realloc-aware comparison of pre- and post-transaction `RentPaying` data sizes and rejects rent-paying-to-rent-paying transitions when the size changed.

## Observed Patch Facts

1. In `runtime/src/account_rent_state.rs`, the patch replaces `for post_rent_state in RentState::into_enum_iter() {` with `let post_rent_state = RentState::Uninitialized;`.

2. In `runtime/src/bank.rs`, the patch adds `#[derive(Serialize, Deserialize)]`.

3. In `sdk/src/system_transaction.rs`, the patch replaces `/// Create and sign new system_instruction::Assign transaction` with `/// Create and sign new SystemInstruction::Allocate transaction`.

4. In `runtime/src/account_rent_state.rs`, the patch replaces `pub(crate) fn transition_allowed_from(&self, pre_rent_state: &RentState) -> bool {` with `pub(crate) fn transition_allowed_from(`.

## Project Context

The changed code sits primarily in `runtime/src`, `sdk/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/accounts.rs`, `sdk/src/transport.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/accounts.rs`, `runtime/src/bank/transaction_account_state_info.rs`. The strongest project-level identifiers around this patch are `Self::RentPaying`, `RentState`, `RentPaying`, and `RentState::RentPaying`.

## Before/After Behavior

Before the patch, `transition_allowed_from` only checked whether a post-transaction `RentPaying` account had also been `RentPaying` before processing. The supplied evidence does not show any size-sensitive check. After the patch, `RentPaying` carries a data size, and when realloc support is enabled a `RentPaying(pre_size)` to `RentPaying(post_size)` transition is allowed only if the sizes match.

# Root Cause

The old rent-state transition rule was too coarse: it tracked the rent-paying classification but not the data size associated with that classification. That left resized rent-paying accounts outside the intended rent-exemption requirement shown by the patch comment and commit subject.

## Walkthrough

1. `RentState::from_account` classifies underfunded nonzero accounts with data as `RentPaying(account.data().len())`.

2. The old transition rule rejected only transitions into `RentPaying` from a non-`RentPaying` pre-state.

3. The patch changes `transition_allowed_from` to accept `do_support_realloc` and compare pre/post data sizes for `RentPaying` states.

4. When realloc support is active, a rent-paying account may remain rent-paying only if `post_data_size == pre_data_size`.

5. Tests were updated from broad enum iteration to explicit rent-state cases that include `RentPaying(size)`.

6. The added mock realloc instruction and SDK allocate helper are support/test code for resized-account scenarios, not the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/account_rent_state.rs | 31 | Defines post-transaction rent-state transition rules and adds data-size comparison for RentPaying accounts. |
| runtime/src/account_rent_state.rs | 138 | Regression coverage for allowed and disallowed rent-state transitions after the rule change. |
| runtime/src/bank/transaction_account_state_info.rs | 1 | Transaction account state tracking path that imports check_rent_state and RentState for pre/post execution validation. |
| runtime/src/accounts.rs | 1 | Runtime accounts path importing check_rent_state, indicating the rule is applied in account processing/storage flow. |
| runtime/src/bank.rs | 17284 | Test-only mock realloc instruction used to exercise resized-account behavior. |
| sdk/src/system_transaction.rs | 28 | SDK transaction helper for SystemInstruction::Allocate, supporting tests or callers that create resized account transactions. |

## Code Snippets

## Snippet 1

Context: `runtime/src/account_rent_state.rs:138` (changes the branch that decides whether execution stops or continues)

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

Context: `runtime/src/bank.rs:17284` (changes signature or replay validation logic)

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

Context: `runtime/src/account_rent_state.rs:31` (changes a sensitive control or state-update path)

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

Make the transition validation carry the missing state dimension, then reject transitions that violate the invariant at the rent-state boundary.

## How It Was Fixed

The patch makes rent-paying state size-aware and updates the transition check so resized rent-paying accounts cannot pass validation as merely legacy rent-paying accounts when realloc support is enabled. It also updates tests and support helpers around allocation/reallocation scenarios.

# Why It Matters

1. Prevents resized accounts from remaining underfunded rent-paying accounts after execution.

2. Keeps runtime account-state validation aligned with Solana rent rules.

3. Protects a protocol resource-accounting invariant rather than proving a crash, theft, or signature bypass.

# Evidence Notes

Supported by `runtime/src/account_rent_state.rs`, where `RentPaying` includes data size and `transition_allowed_from` rejects size changes under realloc-aware execution. `runtime/src/bank.rs` and `sdk/src/system_transaction.rs` appear to add test/support helpers. The supplied evidence does not establish a node crash, panic, unauthorized transfer, signature bypass, or consensus split. Exact feature activation semantics for `do_support_realloc` are not fully shown, so confidence is medium rather than high. Protocol security invariant: A rent-paying account may remain rent-paying after transaction execution only under the allowed legacy condition. With realloc support active, a rent-paying account that changes data size must not remain rent-paying; it must become rent-exempt or fail rent-state validation. Verification notes: The patch does not prove a node crash or panic condition. The patch does not prove unauthorized balance movement or signature bypass. The patch does not prove a consensus split from the provided evidence alone. The bank.rs and sdk helper changes appear test/support related, not the core enforcement point. The exact activation semantics of do_support_realloc are not fully shown in the supplied context. Primary enforcement evidence is in `runtime/src/account_rent_state.rs`. Context connects `RentState` and `check_rent_state` to runtime transaction/account-state validation paths. Helper additions should not be treated as the vulnerable code path. Impact is best stated as a rent/resource-accounting invariant violation, not a proven denial of service or fund loss. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rent-resource-accounting-invariant`
Final impact type: `resource-accounting-invariant`
Final tags: `infrastructure, transaction-processing, rent-validation, account-reallocation, resource-accounting`

The supplied patch evidence supports a conservative security-hardening classification: the runtime rent-state transition rule becomes size-aware and rejects resized accounts that remain rent-paying when realloc support is active. This tightens a protocol resource-accounting invariant in transaction/account validation, but the evidence does not prove a concrete exploit, liveness failure, signature issue, unauthorized transfer, or consensus split.

## Security Evidence

1. Commit subject states resized accounts must be rent exempt.
2. RentState::from_account classifies underfunded accounts with data as RentPaying(data_size).
3. transition_allowed_from now receives do_support_realloc and compares pre/post RentPaying data sizes.
4. When realloc support is active, RentPaying to RentPaying is allowed only if the data size is unchanged.
5. Related context connects RentState/check_rent_state to runtime transaction/account-state validation paths.

## Missing Evidence

1. No demonstrated attacker-controlled exploit path is shown.
2. No evidence of fund theft, signature bypass, privilege escalation, panic, or node crash is provided.
3. No proof of consensus divergence or network-wide liveness impact is provided.
4. Feature activation semantics for do_support_realloc are only partially shown.
5. bank.rs and sdk changes appear to be test/support helpers rather than direct vulnerable behavior.

## Claim Boundaries

1. Treat as protocol resource-accounting hardening, not a proven exploitable vulnerability.
2. Do not retain the original liveness-failure or signature-related framing.
3. Core evidence is limited to rent-state validation around resized rent-paying accounts.
4. Impact should be described as preventing violation of rent-exemption/resource-accounting rules.
