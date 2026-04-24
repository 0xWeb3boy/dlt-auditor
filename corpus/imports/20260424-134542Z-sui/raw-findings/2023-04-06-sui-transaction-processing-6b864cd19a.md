---
case_id: case_20230406_6b864cd19a
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2023-04-06
source_refs:
  - git:6b864cd19a444d4c9b3ef4a0b4d7bf05864a2325
  - "crates/sui-types/src/gas_model/gas_v2.rs:420"
  - "crates/sui-types/src/storage.rs:698"
  - "crates/sui-adapter/src/programmable_transactions/context.rs:714"
  - "crates/sui-types/src/temporary_store.rs:509"
bug_class: incomplete-ownership-validation
impact_type:
  - state-integrity
tags:
  - transaction-processing
  - gas-validation
  - ownership-validation
  - immutable-object-deletion
  - protocol-invariant
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes an incomplete gas-object ownership check in Sui transaction validation. Previously, only the primary gas object was required to have `Owner::AddressOwner`; additional gas objects in `more_gas_objs` were not checked by the same validation. The commit states that an immutable gas coin could therefore reach gas smashing and be deleted, violating the invariant that immutable objects are not deleted.

## Observed Patch Facts

1. In `crates/sui-types/src/gas_model/gas_v2.rs`, the patch replaces `// 1. Gas object has an address owner.` with `// 1. All gas objects have an address owner`.

2. In `crates/sui-types/src/storage.rs`, the patch adds `impl Display for DeleteKind {`.

3. In `crates/sui-adapter/src/programmable_transactions/context.rs`, the patch replaces `Some(metadata) => metadata.version,` with `Some(metadata) => {`.

4. In `crates/sui-types/src/temporary_store.rs`, the patch replaces `// Check it is not read-only` with `// TODO: promote this to an on-in-prod check that raises an invariant_violation`.

## Project Context

The changed code sits primarily in `crates/sui-types/src/gas_model`, `crates/sui-types/src`, `crates/sui-types`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-types/src/object.rs`, `crates/sui-types/src/gas_model/gas_v1.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/gas_model/gas_v1.rs`, `crates/sui-types/src/object.rs`. The strongest project-level identifiers around this patch are `owner`, `Owner::AddressOwner`, `UserInputError::GasObjectNotOwnedObject`, and `object`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/messages_tests.rs`, `crates/sui-types/src/unit_tests/event_filter_tests.rs`.

## Before/After Behavior

Before the change, `check_gas_balance` checked only `gas_object.owner` and returned `UserInputError::GasObjectNotOwnedObject` if that primary gas object was not address-owned. Additional gas objects were still included in aggregate gas balance handling but were not covered by this owner check. After the change, validation iterates over `more_gas_objs.iter().chain(iter::once(&gas_object))` and applies the same address-owner requirement to every gas object. The patch also adds downstream invariant checks around deletion of immutable objects and improves debug reporting for immutable deletion attempts.

# Root Cause

The root cause was incomplete validation of gas-object ownership. The validation path enforced the address-owner requirement for the primary gas object but omitted the additional gas objects, allowing an immutable gas coin to pass this specific check and later be handled by gas-smashing deletion logic.

## Walkthrough

1. Transaction gas validation receives a primary `gas_object` and additional gas objects in `more_gas_objs`.

2. The old code checked only the primary `gas_object.owner` against `Owner::AddressOwner`.

3. Additional gas objects were not checked by that ownership validation even though they were later considered together for gas balance.

4. The commit message states that shared or object-owned gas coins were handled correctly, but an immutable gas coin could be deleted by gas smashing.

5. The fix loops over all gas objects and rejects any object whose owner is not `Owner::AddressOwner`.

6. Execution-effect construction now asserts that deletion metadata for input objects is not immutable.

7. Temporary-store deletion adds debug-time hardening and clearer invariant failure reporting for immutable deletion attempts.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/gas_model/gas_v2.rs | 420 | Primary input validation now requires every gas object, not only the first, to have `Owner::AddressOwner`. |
| crates/sui-adapter/src/programmable_transactions/context.rs | 714 | Execution effect construction asserts that input object metadata for deletions is not immutable. |
| crates/sui-types/src/temporary_store.rs | 509 | Temporary object deletion path adds debug-time hardening against deleting immutable objects, including gas-smashing cases. |
| crates/sui-types/src/storage.rs | 698 | Adds display formatting for `DeleteKind`, supporting clearer invariant failure reporting. |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/gas_model/gas_v2.rs:420` (changes an authorization or privilege gate)

Before
```rust
cost_table: &SuiCostTable,
) -> UserInputResult {
    // 1. Gas object has an address owner.
    if !(matches!(gas_object.owner, Owner::AddressOwner(_))) {
        return Err(UserInputError::GasObjectNotOwnedObject {
            owner: gas_object.owner,
        });
    }
```
After
```rust
cost_table: &SuiCostTable,
) -> UserInputResult {
    // 1. All gas objects have an address owner
    for gas_object in more_gas_objs.iter().chain(iter::once(&gas_object)) {
        if !(matches!(gas_object.owner, Owner::AddressOwner(_))) {
            return Err(UserInputError::GasObjectNotOwnedObject {
                owner: gas_object.owner,
            });
```

## Snippet 2

Context: `crates/sui-types/src/storage.rs:698` (changes a sensitive control or state-update path)

Before
```rust
}
}
```
After
```rust
}
}

impl Display for DeleteKind {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            DeleteKind::Wrap => write!(f, "Wrap"),
            DeleteKind::Normal => write!(f, "Normal"),
```

## Snippet 3

Context: `crates/sui-adapter/src/programmable_transactions/context.rs:714` (changes an authorization or privilege gate)

Before
```rust
for (id, delete_kind) in deletions {
            let version = match input_object_metadata.get(&id) {
                Some(metadata) => metadata.version,
                None => match state_view.get_latest_parent_entry_ref(id) {
                    Ok(Some((_, previous_version, _))) => previous_version,
```
After
```rust
for (id, delete_kind) in deletions {
            let version = match input_object_metadata.get(&id) {
                Some(metadata) => {
                    assert_invariant!(!matches!(metadata.owner, Owner::Immutable), format!("Attempting to delete immutable object {id} via delete kind {delete_kind}"));
                    metadata.version
                }
                None => match state_view.get_latest_parent_entry_ref(id) {
                    Ok(Some((_, previous_version, _))) => previous_version,
```

## Snippet 4

Context: `crates/sui-types/src/temporary_store.rs:509` (changes the branch that decides whether execution stops or continues)

Before
```rust
// there should be no deletion after write
        debug_assert!(self.written.get(id).is_none());
        // Check it is not read-only
        #[cfg(test)] // Movevm should ensure this
        if let Some(object) = self.read_object(id) {
            if object.is_immutable() {
                // This is an internal invariant violation. Move only allows us to
                // mutate objects if they are &mut so they cannot be read-only.
```
After
```rust
// there should be no deletion after write
        debug_assert!(self.written.get(id).is_none());

        // TODO: promote this to an on-in-prod check that raises an invariant_violation
        // Check that we are not deleting an immutable object
        #[cfg(debug_assertions)]
        if let Some(object) = self.read_object(id) {
            if object.is_immutable() {
```

# Fix Pattern

Apply the gas-object ownership invariant uniformly to every gas object accepted by transaction validation, then add downstream invariant checks so deletion of immutable objects is detected if it reaches later execution paths.

## How It Was Fixed

`check_gas_balance` now iterates over both `more_gas_objs` and the primary gas object, returning `GasObjectNotOwnedObject` for any non-address-owned gas object. The execution context now asserts that deletion effects do not target immutable input metadata. The temporary store adds debug-time checks and more detailed panic messages for immutable deletion attempts, supported by `Display` formatting for `DeleteKind`.

# Why It Matters

1. Prevents immutable gas coins from entering the gas-smashing deletion path described by the commit.

2. Preserves the invariant that gas coins used for transaction gas must be address-owned.

3. Protects immutable objects from being represented as deletion effects in this path.

4. Evidence supports unintended immutable gas-object deletion, not theft, arbitrary deletion, or node-wide denial of service.

# Evidence Notes

The strongest evidence is the change in `crates/sui-types/src/gas_model/gas_v2.rs` from checking only `gas_object.owner` to checking every object in `more_gas_objs` plus `gas_object`. The commit message directly explains the bug: only the first gas coin was checked, and an immutable gas coin could be deleted by gas smashing. The assertion in `crates/sui-adapter/src/programmable_transactions/context.rs`, the debug hardening in `crates/sui-types/src/temporary_store.rs`, and `DeleteKind` display support are secondary hardening and diagnostics, not the primary root cause. Protocol security invariant: Every gas object supplied to transaction validation must be address-owned before it can participate in gas accounting, gas smashing, or execution-effect generation. Immutable objects must not be deleted as transaction effects. Verification notes: The patch does not prove theft, balance inflation, or direct fund extraction. The evidence supports unintended deletion of immutable gas objects, not arbitrary object deletion. The evidence does not establish remote unauthenticated exploitability or node-wide denial of service. Shared or object-owned gas coins are described as already handled correctly; the concrete bug shape is immutable gas coin validation. Some deletion checks are hardening/debug assertions and are secondary to the main validation fix. No claim is made for theft, balance inflation, arbitrary object deletion, or remote denial of service. Helper and diagnostic changes are treated as support code, not the root cause. Classification remains security-relevant because the patch prevents an unintended protocol-state deletion of immutable objects. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `incomplete-ownership-validation`
Final impact type: `state-integrity`
Final tags: `transaction-processing, gas-validation, ownership-validation, immutable-object-deletion, protocol-invariant`

The supplied evidence supports keeping this as a security-fix case, but the original liveness framing is misleading. The patch fixes an incomplete ownership validation path for multiple gas coins, where only the primary gas object was checked for address ownership. The commit message and code evidence tie that gap to deletion of an immutable gas coin during gas smashing, which is a protocol/state-integrity invariant violation. The evidence does not support broader claims such as theft, arbitrary object deletion, or denial of service.

## Security Evidence

1. Gas validation changed from checking only the primary gas_object owner to checking every object in more_gas_objs plus the primary gas object.
2. The rejected condition is security-sensitive ownership state: gas objects must be Owner::AddressOwner.
3. Commit body explicitly says an immutable gas coin could be deleted by gas smashing and that this was not intended.
4. Execution context adds an invariant assertion preventing deletion effects for immutable input objects.
5. Temporary store adds debug-time hardening and diagnostics for attempts to delete immutable objects.

## Missing Evidence

1. No proof of theft, balance inflation, or direct fund extraction.
2. No evidence that arbitrary immutable objects could be deleted beyond the gas-coin path described.
3. No evidence of remote unauthenticated exploitability or node-wide denial of service.
4. Some added deletion checks are debug or invariant hardening rather than the primary production rejection path.

## Claim Boundaries

1. Classify as incomplete ownership validation causing possible immutable gas-object deletion.
2. Impact should be limited to protocol state integrity, not liveness.
3. Do not claim arbitrary object deletion or asset theft from the supplied patch alone.
4. Downstream invariant checks are supporting hardening; the primary fix is validating all gas coin owners.
