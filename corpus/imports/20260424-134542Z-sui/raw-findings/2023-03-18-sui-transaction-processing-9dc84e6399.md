---
case_id: case_20230318_9dc84e6399
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-03-18
source_refs:
  - git:9dc84e6399731873408c8b4793b40f07822527e0
  - "crates/sui-adapter/src/execution_engine.rs:114"
  - "crates/sui-types/src/lib.rs:83"
  - "crates/sui-types/src/temporary_store.rs:691"
  - "crates/sui-types/src/lib.rs:109"
bug_class: object-access-authentication-invariant
impact_type:
  - unauthorized-object-read
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - object-authentication
  - ownership-invariant
  - debug-assertion
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds debug-only invariant checking for authenticated object access after transaction execution and before effects are produced. This is security-relevant hardening, but the provided evidence does not establish a concrete production vulnerability or production enforcement change.

## Observed Patch Facts

1. In `crates/sui-adapter/src/execution_engine.rs`, the patch replaces `let (inner, effects) = temporary_store.to_effects(` with `#[cfg(debug_assertions)]`.

2. In `crates/sui-types/src/lib.rs`, the patch replaces `const fn get_hex_address_two() -> AccountAddress {` with `/// Return 'true' if 'id' is a special system package that can be upgraded at epoch b...`.

3. In `crates/sui-types/src/temporary_store.rs`, the patch replaces `impl<S: GetModule + ObjectStore + BackingPackageStore> TemporaryStore<S> {` with `impl<S: ObjectStore> TemporaryStore<S> {`.

4. In `crates/sui-types/src/lib.rs`, the patch removes `pub fn is_system_package(id: ObjectID) -> bool {`.

## Project Context

The changed code sits primarily in `crates/sui-adapter/src`, `crates/sui-adapter`, `crates/sui-types/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-types/src/object.rs`, `crates/sui-types/src/move_package.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-adapter/src/adapter.rs`, `crates/sui-adapter/src/programmable_transactions/execution.rs`. The strongest project-level identifiers around this patch are `ObjectID`, `TransactionDigest::genesis`, `Mode::allow_arbitrary_function_calls`, and `addr`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/base_types_tests.rs`, `crates/sui-types/src/unit_tests/messages_tests.rs`.

## Before/After Behavior

Before the patch, the shown execution path removed the genesis transaction dependency and proceeded toward effect generation without the displayed ownership-authentication invariant check. After the patch, debug builds call `temporary_store.check_ownership_invariants(&transaction_signer, gas, is_epoch_change).unwrap()` unless arbitrary function calls are allowed. The temporary store gains helper logic for computing objects that require authentication and objects already authenticated. `is_system_package` is exposed to classify framework and Move standard library package IDs.

# Root Cause

The grounded issue is an invariant-checking gap in the displayed debug/runtime validation path: the provided before-state evidence does not show an end-of-execution check proving that every accessed object was authenticated from an allowed root. The evidence does not prove that unauthenticated reads were possible in production, nor that such reads could be exploited.

## Walkthrough

1. `execute_transaction_to_effects` runs transaction execution and computes status/results.

2. The code removes `TransactionDigest::genesis()` from transaction dependencies.

3. The patch inserts a `#[cfg(debug_assertions)]` block before effect materialization.

4. In normal modes, that block calls `TemporaryStore::check_ownership_invariants` with the signer, gas objects, and epoch-change flag.

5. The check is skipped when `Mode::allow_arbitrary_function_calls()` is true, described as dev inspect mode.

6. `TemporaryStore` gains helper logic for separating objects that require authentication from objects already authenticated.

7. `is_system_package` identifies the Move standard library and Sui framework package IDs for special handling.

8. Because the call is debug-only, the shown patch catches invariant violations during debug execution but does not establish production rejection behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-adapter/src/execution_engine.rs | 114 | Runs the ownership invariant check after transaction execution and before converting the temporary store into effects, excluding arbitrary-function-call/dev-inspect mode. |
| crates/sui-types/src/temporary_store.rs | 691 | Computes authenticated object roots and objects requiring authentication from transaction input objects, gas objects, and ownership state. |
| crates/sui-types/src/lib.rs | 83 | Defines the system package classifier used by object/package ownership and epoch-change exception logic. |

## Code Snippets

## Snippet 1

Context: `crates/sui-adapter/src/execution_engine.rs:114` (changes the branch that decides whether execution stops or continues)

Before
```rust
transaction_dependencies.remove(&TransactionDigest::genesis());

    let (inner, effects) = temporary_store.to_effects(
        shared_object_refs,
```
After
```rust
transaction_dependencies.remove(&TransactionDigest::genesis());

    #[cfg(debug_assertions)]
    {
        if !Mode::allow_arbitrary_function_calls() {
            temporary_store
                .check_ownership_invariants(&transaction_signer, gas, is_epoch_change)
                .unwrap()
```

## Snippet 2

Context: `crates/sui-types/src/lib.rs:83` (changes a sensitive control or state-update path)

Before
```rust
pub const SUI_CLOCK_OBJECT_SHARED_VERSION: SequenceNumber = OBJECT_START_VERSION;

const fn get_hex_address_two() -> AccountAddress {
    let mut addr = [0u8; AccountAddress::LENGTH];
```
After
```rust
pub const SUI_CLOCK_OBJECT_SHARED_VERSION: SequenceNumber = OBJECT_START_VERSION;

/// Return `true` if `id` is a special system package that can be upgraded at epoch boundaries
/// All new system package ID's must be added here
pub fn is_system_package(id: ObjectID) -> bool {
    matches!(id, MOVE_STDLIB_OBJECT_ID | SUI_FRAMEWORK_OBJECT_ID)
}
```

## Snippet 3

Context: `crates/sui-types/src/temporary_store.rs:691` (changes an authorization or privilege gate)

Before
```rust
}

impl<S: GetModule + ObjectStore + BackingPackageStore> TemporaryStore<S> {
    /// Check that this transaction neither creates nor destroys SUI. This should hold for all txes except
```
After
```rust
}

impl<S: ObjectStore> TemporaryStore<S> {
    /// returns lists of (objects whose owner we must authenticate, objects whose owner has already been authenticated)
    fn get_objects_to_authenticate(
        &self,
        sender: &SuiAddress,
        gas: &[ObjectRef],
```

## Snippet 4

Context: `crates/sui-types/src/lib.rs:109` (changes a sensitive control or state-update path)

Before
```rust
}

pub fn is_system_package(id: ObjectID) -> bool {
    matches!(id, MOVE_STDLIB_OBJECT_ID | SUI_FRAMEWORK_OBJECT_ID)
}

fn resolve_address(addr: &str) -> Option<AccountAddress> {
    match addr {
```
After
```rust
}

fn resolve_address(addr: &str) -> Option<AccountAddress> {
    match addr {
```

# Fix Pattern

Add a post-execution invariant assertion at a security-sensitive boundary, deriving authentication roots from transaction context and validating accessed objects against those roots.

## How It Was Fixed

The execution engine invokes `check_ownership_invariants` in debug builds before converting the temporary store into effects. Supporting temporary-store logic computes authentication state from inputs, gas objects, ownership relationships, and system or epoch context. A system-package classifier was moved or exposed for consistent special-case handling.

# Why It Matters

1. Object access authentication is a core transaction safety property.

2. Debug assertions can catch invariant violations during development and testing.

3. The patch documents expected authentication roots for transaction object reads.

4. The evidence does not show production enforcement or a concrete exploit.

# Evidence Notes

Supported by the added debug-only call in `crates/sui-adapter/src/execution_engine.rs`, the new authentication helper logic in `crates/sui-types/src/temporary_store.rs`, and the `is_system_package` helper in `crates/sui-types/src/lib.rs`. The commit message explicitly frames the change as preserving a security property. Unsupported claims removed: malformed input handling, panic-prone decoding, denial of service, consensus impact, and confirmed exploitable unauthenticated reads. Protocol security invariant: A Sui transaction should only read objects whose access can be authenticated from allowed roots such as the signer, gas/input objects, shared or immutable objects, system/epoch exceptions, or objects indirectly owned by an authenticated object. Verification notes: The patch does not prove a concrete externally exploitable transaction exists. The new enforcement shown is debug-only, so production rejection behavior is not established by the provided diff. The evidence does not support the heuristic baseline claim of panic-prone malformed input or denial of service. The patch verifies an invariant after execution; it does not by itself show where an unauthenticated read would originate. Test updates demonstrate coverage for dynamic-field/object cases but do not prove full consensus impact. No concrete exploit path is shown in the provided evidence. The enforcement shown is gated by `#[cfg(debug_assertions)]`. The `.unwrap()` is part of a debug assertion path, not evidence of a production error-handling fix. Test files were updated, but their contents are not provided in enough detail to prove a vulnerability regression. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `object-access-authentication-invariant`
Final impact type: `unauthorized-object-read`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, object-authentication, ownership-invariant, debug-assertion, security-hardening`

The evidence supports retaining this as security hardening, not as a concrete production security fix. The commit explicitly frames authenticated object reads as a key transaction security property, and the patch adds a post-execution ownership/authentication invariant check in the transaction effects path. However, the shown enforcement is gated by debug assertions, so the patch does not prove a production exploit was fixed or that invalid transactions are rejected in release builds.

## Security Evidence

1. Commit message explicitly identifies authenticated object reads as a key security property of Sui transactions.
2. Execution path now calls check_ownership_invariants before effects are produced.
3. TemporaryStore gains logic to determine objects requiring authentication versus already authenticated objects.
4. The check is skipped only for arbitrary-function-call/dev-inspect mode in the shown code.

## Missing Evidence

1. No concrete exploit path or externally triggerable unauthenticated read is shown.
2. The added check is #[cfg(debug_assertions)], so production enforcement is not established.
3. Provided test evidence is not detailed enough to prove a vulnerability regression.
4. No evidence supports the original liveness-failure classification.

## Claim Boundaries

1. Validate as security hardening for transaction object-access invariant checking.
2. Do not claim a confirmed production vulnerability or consensus break from this evidence alone.
3. Do not classify as liveness impact based on the supplied patch.
4. Do not treat the debug-only unwrap as a production error-handling security fix.
