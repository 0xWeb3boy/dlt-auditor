---
case_id: case_20221108_d8fef9cd19
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2022-11-08
source_refs:
  - git:d8fef9cd19a5bfe2efbbbeb078d6dda2966e0302
  - "crates/sui-framework/src/natives/object_runtime/mod.rs:130"
  - "crates/sui-framework/src/natives/transfer.rs:91"
  - "crates/sui-framework/src/natives/transfer.rs:106"
  - "crates/sui-framework/src/natives/object_runtime/mod.rs:83"
bug_class: ownership-invariant-enforcement
tags:
  - infrastructure
  - storage
  - object-ownership
  - shared-objects
  - state-integrity
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Sui's native shared-object transfer path from an unconditional successful transfer record into a classified transfer result. `share_object` now rejects `OwnerChanged` with `E_SHARED_NON_NEW_OBJECT`, enforcing that non-new objects are not converted into shared ownership. The evidence supports an ownership-invariant fix, but not a demonstrated exploit, asset theft, or consensus impact.

## Observed Patch Facts

1. In `crates/sui-framework/src/natives/object_runtime/mod.rs`, the patch replaces `) -> PartialVMResult<()> {` with `) -> PartialVMResult<TransferResult> {`.

2. In `crates/sui-framework/src/natives/transfer.rs`, the patch replaces `Ok(NativeResult::ok(cost, smallvec![]))` with `Ok(match transfer_result {`.

3. In `crates/sui-framework/src/natives/transfer.rs`, the patch replaces `) -> PartialVMResult<()> {` with `) -> PartialVMResult<TransferResult> {`.

4. In `crates/sui-framework/src/natives/object_runtime/mod.rs`, the patch replaces `impl TestInventories {` with `pub enum TransferResult {`.

## Project Context

The changed code sits primarily in `crates/sui-framework/src/natives/object_runtime`, `crates/sui-framework/src/natives`, `crates/sui-framework/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/sui-framework/src/natives/types.rs`, `crates/sui-framework/src/natives/tx_context.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-framework/src/natives/types.rs`, `crates/sui-framework/src/natives/tx_context.rs`. The strongest project-level identifiers around this patch are `TransferResult`, `NativeResult::ok`, `TransferResult::New`, and `PartialVMResult`.

## Before/After Behavior

Before the patch, `ObjectRuntime::transfer` returned only `PartialVMResult<()>`, inserted the transfer, and `share_object` returned success after the runtime transfer completed. After the patch, transfer returns `TransferResult::{New, SameOwner, OwnerChanged}` and `share_object` succeeds only for `New` or `SameOwner`, aborting on `OwnerChanged`.

# Root Cause

The shared-object native path did not expose enough ownership classification to `share_object`; as a result, `share_object` could not distinguish a valid newly created shared object from a transfer that changed an existing object's owner to `Shared`.

## Walkthrough

1. A Move native call reaches `share_object` with an object value to be shared.

2. `share_object` calls `object_runtime_transfer` using `Owner::Shared`.

3. Before the fix, the runtime transfer path recorded the transfer and returned only success or VM error.

4. That meant `share_object` had no local result indicating whether the object was newly created or owner-changing.

5. The patch adds `TransferResult` and classifies transfers using `new_ids`, the system-state object exception, and prior owner information from `input_objects`.

6. `object_runtime_transfer` propagates that classification back to `share_object`.

7. `share_object` returns success for `New` and `SameOwner`, and aborts with `E_SHARED_NON_NEW_OBJECT` for `OwnerChanged`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-framework/src/natives/object_runtime/mod.rs | 83 | Defines TransferResult states used to distinguish newly created, same-owner, and owner-changed transfers. |
| crates/sui-framework/src/natives/object_runtime/mod.rs | 126 | Classifies object transfers by checking new_ids, the system state object exception, and previous owners from input_objects. |
| crates/sui-framework/src/natives/transfer.rs | 72 | Implements native share_object and turns OwnerChanged transfer results into an abort. |
| crates/sui-framework/src/natives/transfer.rs | 103 | Propagates TransferResult from object_runtime_transfer to callers such as share_object. |

## Code Snippets

## Snippet 1

Context: `crates/sui-framework/src/natives/object_runtime/mod.rs:130` (changes an authorization or privilege gate)

Before
```rust
tag: StructTag,
        obj: Value,
    ) -> PartialVMResult<()> {
        let id: ObjectID = get_object_id(obj.copy_value()?)?
            .value_as::<AccountAddress>()?
            .into();
        self.state.transfers.insert(id, (owner, ty, tag, obj));
        Ok(())
```
After
```rust
tag: StructTag,
        obj: Value,
    ) -> PartialVMResult<TransferResult> {
        let id: ObjectID = get_object_id(obj.copy_value()?)?
            .value_as::<AccountAddress>()?
            .into();
        // - an object is new if it is contained in the new ids or if it is the
        //   SUI_SYSTEM_STATE_OBJECT_ID which is only transferred in genesis
```

## Snippet 2

Context: `crates/sui-framework/src/natives/transfer.rs:91` (changes a sensitive control or state-update path)

Before
```rust
)?;
    let cost = legacy_emit_cost();
    Ok(NativeResult::ok(cost, smallvec![]))
}
```
After
```rust
)?;
    let cost = legacy_emit_cost();
    Ok(match transfer_result {
        // New means the ID was created in this transaction
        // SameOwner means the object was previously shared and was re-shared; since
        // shared objects cannot be taken by-value in the adapter, this can only
        // happen via test_scenario
        TransferResult::New | TransferResult::SameOwner => NativeResult::ok(cost, smallvec![]),
```

## Snippet 3

Context: `crates/sui-framework/src/natives/transfer.rs:106` (changes a sensitive control or state-update path)

Before
```rust
ty: Type,
    obj: Value,
) -> PartialVMResult<()> {
    let tag = match context.type_to_type_tag(&ty)? {
        TypeTag::Struct(s) => s,
```
After
```rust
ty: Type,
    obj: Value,
) -> PartialVMResult<TransferResult> {
    let tag = match context.type_to_type_tag(&ty)? {
        TypeTag::Struct(s) => s,
```

## Snippet 4

Context: `crates/sui-framework/src/natives/object_runtime/mod.rs:83` (changes a sensitive control or state-update path)

Before
```rust
}

impl TestInventories {
    fn new() -> Self {
```
After
```rust
}

pub enum TransferResult {
    New,
    SameOwner,
    OwnerChanged,
}
```

# Fix Pattern

Return structured classification from the lower-level transfer routine and enforce the ownership invariant at the native shared-object API boundary.

## How It Was Fixed

The patch adds `TransferResult` in `crates/sui-framework/src/natives/object_runtime/mod.rs`, changes `ObjectRuntime::transfer` and `object_runtime_transfer` to return it, and updates `crates/sui-framework/src/natives/transfer.rs` so `share_object` rejects `OwnerChanged` instead of always returning `NativeResult::ok`.

# Why It Matters

1. Enforces a core object ownership invariant in the Move/Sui shared-object path.

2. Prevents owner-changing transfers from being accepted as valid shared-object creation.

3. Evidence supports invariant bypass prevention, not specific exploit impact.

# Evidence Notes

Grounded evidence is limited to the provided hunks and commit message. The commit explicitly says shared objects must be newly created and `sui::transfer::shared` should abort if the object is not new. The code adds `TransferResult`, classifies transfers, and maps `OwnerChanged` to `E_SHARED_NON_NEW_OBJECT`. The evidence does not establish remote reachability, concrete transaction construction, asset theft, privilege escalation, or consensus failure. Protocol security invariant: Objects passed to `sui::transfer::shared` must be newly created in the current transaction, with the documented system-state exception and same-owner re-sharing path. A transfer that changes a non-new object's owner to `Shared` must abort. Verification notes: The patch does not prove remote exploitability or transaction construction details. The patch does not show whether ordinary adapters could pass previously shared objects by value outside test_scenario. The patch does not prove asset theft, privilege escalation, or consensus failure. The classification is based on ownership-invariant enforcement, not on a demonstrated end-to-end attack. Implementation evidence is from `object_runtime/mod.rs` and `transfer.rs` hunks only. Tests were mentioned in the changed file list but no test assertions were provided in the input. Confidence is medium because the invariant enforcement is clear, while exploitability and impact are not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ownership-invariant-enforcement`
Final tags: `infrastructure, storage, object-ownership, shared-objects, state-integrity, security-hardening`

The supplied evidence clearly shows a security-sensitive ownership invariant being tightened: `sui::transfer::shared` now aborts when a non-new object would become shared, rather than unconditionally accepting the transfer. That supports retaining the case as security hardening. The patch does not prove a concrete exploitable vulnerability, asset theft, privilege escalation, or consensus impact, so `security-fix` and the broader `state-corruption` framing are too strong.

## Security Evidence

1. Commit message states shared objects must be newly created and non-new shared transfers should abort.
2. `ObjectRuntime::transfer` now returns `TransferResult` instead of only success, classifying new, same-owner, and owner-changed transfers.
3. `share_object` now maps `TransferResult::OwnerChanged` to `E_SHARED_NON_NEW_OBJECT` instead of always returning success.
4. The changed path controls object ownership transition into shared ownership, a security-sensitive state invariant in Sui.

## Missing Evidence

1. No provided evidence of an end-to-end exploit or attacker-controlled transaction sequence.
2. No proof of asset theft, unauthorized access, privilege escalation, or consensus failure.
3. No test assertions are included in the supplied evidence despite test files being changed.
4. Reachability for ordinary non-test adapters is only partially indicated by comments, not fully proven.

## Claim Boundaries

1. Validate only as ownership-invariant hardening for shared-object transfers.
2. Do not claim demonstrated state corruption beyond the rejected owner-changing shared transfer condition.
3. Do not claim concrete exploitability or financial impact from the provided patch alone.
4. Do not rely on issue #5835 contents because they were not supplied.
