---
case_id: case_20190829_6b6cbd3f36
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: medium
date: 2019-08-29
source_refs:
  - git:6b6cbd3f3668992f0971259d46b6599b650f9a19
  - "src/vm/types/mod.rs:156"
  - "src/vm/types/mod.rs:175"
  - "src/vm/types/serialization.rs:420"
  - "src/vm/types/serialization.rs:440"
bug_class: missing-constructor-validation
impact_type:
  - resource-exhaustion
confidence: medium
tags:
  - vm
  - type-validation
  - size-limit
  - constructor-invariant
  - resource-exhaustion
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Clarity VM list type/value construction to rely on constructor-validated ListTypeData/TypeSignature metadata instead of direct field construction and repeated downstream size checks. This supports an invariant-cleanup or hardening interpretation around MAX_VALUE_SIZE, but the supplied evidence does not establish an externally reachable vulnerability or concrete security impact.

## Observed Patch Facts

1. In `src/vm/types/mod.rs`, the patch replaces `if expected_type.size()? > MAX_VALUE_SIZE {` with `// Constructors for TypeSignature ensure that the size of the Value cannot`.

2. In `src/vm/types/mod.rs`, the patch replaces `let type_sig = TypeSignature::construct_parent_list_type(&list_data)?;` with `// Constructors for TypeSignature ensure that the size of the Value cannot`.

3. In `src/vm/types/serialization.rs`, the patch replaces `ListTypeData { max_len: 3, dimension: 2, atomic_type: AtomTypeIdentifier::BoolType })...` with `ListTypeData::new_list(BoolType, 3, 2).unwrap())).unwrap_err(),`.

4. In `src/vm/types/serialization.rs`, the patch replaces `ListTypeData { max_len: 3, dimension: 3, atomic_type: AtomTypeIdentifier::IntType }))...` with `ListTypeData::new_list(IntType, 3, 3).unwrap())).unwrap_err() {`.

## Project Context

The changed code sits primarily in `src/vm/types`, `src/vm`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/vm/types/signatures.rs`, `src/vm/analysis/type_checker/natives/lists.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/vm/types/signatures.rs`, `src/vm/analysis/type_checker/natives/lists.rs`. The strongest project-level identifiers around this patch are `Value`, `TypeSignature`, `Value::try_deserialize`, and `TypeSignature::List`. Nearby tests or test-like files include `src/vm/analysis/type_checker/tests/mod.rs`, `src/vm/tests/simple_apply_eval.rs`.

## Before/After Behavior

Before, Value::list_with_type checked expected_type.size()? > MAX_VALUE_SIZE and accessed expected_type.max_len directly, while tests manually built ListTypeData with struct literals. Value::list_from also performed a local MAX_VALUE_SIZE check after constructing a TypeSignature. After, Value construction comments state that TypeSignature constructors enforce the size limit, list length uses expected_type.get_max_len(), and tests use ListTypeData::new_list(...).unwrap().

# Root Cause

The supported root cause is inconsistent enforcement of the ListTypeData/TypeSignature construction invariant: some code and tests could assemble or consume list type metadata directly instead of using the constructor intended to guard computed type size. The evidence does not prove that this was attacker reachable or exploitable.

## Walkthrough

1. Value::list_with_type previously performed a local expected_type.size()? > MAX_VALUE_SIZE check.

2. The patched Value::list_with_type removes that local check and documents that TypeSignature constructors enforce MAX_VALUE_SIZE.

3. The same function switches from direct expected_type.max_len access to expected_type.get_max_len().

4. Value::list_from previously constructed a parent list TypeSignature and then checked its size locally.

5. The patched path relies on TypeSignature::construct_parent_list_type to reject oversized type signatures.

6. Serialization tests previously used raw ListTypeData struct literals for nested list expectations.

7. The tests now use ListTypeData::new_list(...).unwrap(), showing the intended construction path is the guarded API.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/vm/types/mod.rs | 156 | Value::list_with_type trusts constructed ListTypeData and checks list length/type admission using accessor methods |
| src/vm/types/mod.rs | 175 | Value::list_from relies on TypeSignature::construct_parent_list_type to reject oversized constructed list types |
| src/vm/types/serialization.rs | 420 | deserialization tests now construct expected ListTypeData through guarded constructor for nested list type checks |
| src/vm/types/serialization.rs | 440 | deserialization tests now use guarded constructor for dimensional list type expectations |
| src/vm/types/signatures.rs | 1 | TypeSignature/ListTypeData subsystem context where constructor-enforced size limits are anchored |

## Code Snippets

## Snippet 1

Context: `src/vm/types/mod.rs:156` (changes a sensitive control or state-update path)

Before
```rust
///  that any typing data is correct.
    pub fn list_with_type(list_data: Vec<Value>, expected_type: ListTypeData) -> Result<Value> {
        if expected_type.size()? > MAX_VALUE_SIZE {
            return Err(RuntimeErrorType::ValueTooLarge.into())
        }

        if (expected_type.max_len as usize) < list_data.len() {
            return Err(InterpreterError::FailureConstructingListWithType.into())
```
After
```rust
///  that any typing data is correct.
    pub fn list_with_type(list_data: Vec<Value>, expected_type: ListTypeData) -> Result<Value> {
        // Constructors for TypeSignature ensure that the size of the Value cannot
        //   be greater than MAX_VALUE_SIZE (they error on such constructions)
        //   so we do not need to perform that check here.
        if (expected_type.get_max_len() as usize) < list_data.len() {
            return Err(InterpreterError::FailureConstructingListWithType.into())
        }
```

## Snippet 2

Context: `src/vm/types/mod.rs:175` (changes a sensitive control or state-update path)

Before
```rust
pub fn list_from(list_data: Vec<Value>) -> Result<Value> {
        let type_sig = TypeSignature::construct_parent_list_type(&list_data)?;
        // Aaron: at this point, we've _already_ allocated memory for this type.
        //     (e.g., from a (map...) call, or a (list...) call.
        //     this is a problem _if_ the static analyzer cannot already prevent
        //     this case. This applies to all the constructor size checks.
        if type_sig.size()? > MAX_VALUE_SIZE {
```
After
```rust
pub fn list_from(list_data: Vec<Value>) -> Result<Value> {
        // Constructors for TypeSignature ensure that the size of the Value cannot
        //   be greater than MAX_VALUE_SIZE (they error on such constructions)
        // Aaron: at this point, we've _already_ allocated memory for this type.
        //     (e.g., from a (map...) call, or a (list...) call.
        //     this is a problem _if_ the static analyzer cannot already prevent
        //     this case. This applies to all the constructor size checks.
```

## Snippet 3

Context: `src/vm/types/serialization.rs:420` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert_eq!(Value::try_deserialize(
            serialized_0, &TypeSignature::List(
                ListTypeData { max_len: 3, dimension: 2, atomic_type: AtomTypeIdentifier::BoolType })).unwrap_err(),
                   InterpreterError::DeserializeExpected(
                       TypeSignature::Atom(AtomTypeIdentifier::BoolType)).into());
```
After
```rust
assert_eq!(Value::try_deserialize(
            serialized_0, &TypeSignature::List(
                ListTypeData::new_list(BoolType, 3, 2).unwrap())).unwrap_err(),
                   InterpreterError::DeserializeExpected(
                       TypeSignature::Atom(AtomTypeIdentifier::BoolType)).into());
```

## Snippet 4

Context: `src/vm/types/serialization.rs:440` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert!(match Value::try_deserialize(
            serialized_1, &TypeSignature::List(
                ListTypeData { max_len: 3, dimension: 3, atomic_type: AtomTypeIdentifier::IntType })).unwrap_err() {
            Error::Interpreter(InterpreterError::DeserializeExpected(_)) => true,
            _ => false
```
After
```rust
assert!(match Value::try_deserialize(
            serialized_1, &TypeSignature::List(
                ListTypeData::new_list(IntType, 3, 3).unwrap())).unwrap_err() {
            Error::Interpreter(InterpreterError::DeserializeExpected(_)) => true,
            _ => false
```

# Fix Pattern

Centralize size validation in ListTypeData/TypeSignature constructors and update callers/tests to use accessors and constructor APIs instead of raw fields or duplicate downstream checks.

## How It Was Fixed

The patch removes duplicated MAX_VALUE_SIZE checks from Value list construction, uses get_max_len() for list length validation, and updates deserialization tests to construct ListTypeData through new_list().

# Why It Matters

1. Maintains a single canonical boundary for list type size validation.

2. Reduces risk of inconsistent MAX_VALUE_SIZE handling across VM list construction paths.

3. May be security relevant if oversized type metadata is externally reachable, but that reachability is not shown.

# Evidence Notes

Grounded evidence is limited to Value::list_with_type, Value::list_from, and serialization test changes. The commit subject supports the constructor-validation interpretation. The draft's claims about security hardening are plausible but not established by concrete exploitability, attacker control, consensus impact, asset impact, authentication impact, cryptographic impact, or memory-safety impact. Protocol security invariant: VM list type metadata should be constructed through APIs that enforce MAX_VALUE_SIZE before Value construction relies on that metadata. Verification notes: No external attacker-controlled entry point is proven by the provided patch evidence. No consensus, asset-theft, authentication, or cryptographic failure is shown. No memory safety violation is demonstrated; the evidence supports a bounded-size invariant issue. The patch may also be API cleanup by removing direct ListTypeData construction; security impact depends on whether unguarded construction was reachable outside trusted code. No external input path is demonstrated in the supplied evidence. No failing regression test for an oversized malicious ListTypeData is shown. No concrete security consequence is shown beyond MAX_VALUE_SIZE invariant enforcement. Exclude from the security corpus unless additional evidence proves attacker-reachable impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-constructor-validation`
Final impact type: `resource-exhaustion`
Final confidence: `medium`
Final tags: `vm, type-validation, size-limit, constructor-invariant, resource-exhaustion`

The supplied evidence supports security hardening rather than a concrete security fix. The commit and patch move ListTypeData use toward constructor-enforced MAX_VALUE_SIZE invariants and away from raw field construction or duplicated downstream checks. That is plausibly security relevant for VM resource bounds, but the evidence does not prove attacker reachability, exploitability, consensus impact, asset impact, or an actual bypass in production.

## Security Evidence

1. Commit subject explicitly says ListTypeData must call a constructor that guards type size.
2. Value list construction now documents reliance on TypeSignature constructors to reject values above MAX_VALUE_SIZE.
3. Call sites/tests replace raw ListTypeData struct literals with ListTypeData::new_list(...).
4. The touched code is in VM value/type construction and deserialization paths, where size bounds can be security relevant.

## Missing Evidence

1. No shown attacker-controlled path to construct malformed or oversized ListTypeData.
2. No regression test demonstrates an oversized malicious type being rejected after the patch.
3. No concrete denial-of-service, consensus, asset, authentication, cryptographic, or memory-safety impact is demonstrated.
4. The provided diff does not show the ListTypeData definition change that makes constructor use mandatory.

## Claim Boundaries

1. Classify as hardening of VM type-size invariants, not as a proven exploitable vulnerability fix.
2. Do not claim cryptography impact; the evidence is about VM list/type metadata and serialization.
3. Do not claim state corruption or state-integrity impact from the supplied patch alone.
4. The likely impact is bounded to resource exhaustion risk from oversized type/value metadata if such metadata were reachable.
