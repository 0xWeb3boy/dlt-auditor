---
case_id: case_20250707_7f081d66
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: high
date: 2025-07-07
source_refs:
  - git:7f081d6636ce17fc8f29561c3fa852928b294fa7
  - "crates/libzkp/src/lib.rs:49"
  - "crates/libzkp/src/lib.rs:31"
  - "crates/libzkp/src/lib.rs:6"
bug_class: input-validation
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - input-validation
  - fork-name
  - consensus-sensitive
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds fork-name normalization and an equality check in `gen_universal_task`, so chunk and batch tasks no longer proceed with an unchecked combination of `task_json` fork data and a separate fork-name string. The evidence supports a correctness/integrity fix around inconsistent fork-name handling, but it does not establish a concrete vulnerability or prior acceptance of invalid proofs.

## Observed Patch Facts

1. In `crates/libzkp/src/lib.rs`, the patch replaces `let task = serde_json::from_str::<ChunkProvingTask>(task_json)?;` with `let mut task = serde_json::from_str::<ChunkProvingTask>(task_json)?;`.

2. In `crates/libzkp/src/lib.rs`, the patch replaces `fork_name: &str,` with `fork_name_str: &str,`.

3. In `crates/libzkp/src/lib.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `crates/libzkp/src`, `crates/libzkp`, which anchors the finding in the `core-logic` area of the project. Historical context from `crates/libzkp/src/tasks.rs`, `crates/libzkp/src/proofs.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/libzkp/src/proofs.rs`, `crates/libzkp/src/tasks/bundle.rs`. The strongest project-level identifiers around this patch are `fork_name`, `task`, `serde_json::from_str`, and `ForkName::from`.

## Before/After Behavior

Before the change, `gen_universal_task` deserialized chunk or batch tasks and passed the separate fork-name argument into downstream generation without first proving that the task's embedded `fork_name` matched it. After the change, the code parses `task.fork_name` into `ForkName`, rewrites the task field to the canonical string form, asserts equality with `fork_name_str`, and then calls the downstream generator with the typed fork value.

# Root Cause

The function accepted two representations of fork identity, one inside `task_json` and one as a separate string parameter, but did not enforce that they were canonicalized and consistent before invoking fork-specific task generation.

## Walkthrough

1. `gen_universal_task` takes `task_type`, `task_json`, a fork-name string, expected verification material, and an optional interpreter.

2. In the pre-patch chunk path, the code deserialized `ChunkProvingTask` and called `gen_universal_chunk_task(task, fork_name.into(), interpreter)` without a shown comparison against `task.fork_name`.

3. The pre-patch batch path did the same pattern with `BatchProvingTask` and `gen_universal_batch_task(task, fork_name.into())`.

4. The patch imports `ForkName` and renames the parameter to `fork_name_str`, making the string input distinct from the typed enum used internally.

5. For chunk and batch tasks, the patched code deserializes into `mut task`, derives `ForkName::from(task.fork_name.to_lowercase().as_str())`, rewrites `task.fork_name` to the canonical string, and asserts it equals `fork_name_str`.

6. Only after that check does the function call the downstream universal task generator with the typed `ForkName`.

7. Related traced context in `proofs.rs` shows fork-specific public-input handling exists, but the diff alone does not prove a security failure mode beyond inconsistent fork-name handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/libzkp/src/lib.rs | 30 | `gen_universal_task` entrypoint that combines caller-supplied fork context, serialized task JSON, and expected verification material |
| crates/libzkp/src/lib.rs | 49 | Chunk and batch task dispatch now canonicalize `task.fork_name`, overwrite it with canonical text, and assert it matches `fork_name_str` before generating universal tasks |
| crates/libzkp/src/proofs.rs | 182 | Downstream fork-specific public-input hash checking depends on a correct `ForkName`, making fork/task consistency protocol-relevant |

## Code Snippets

## Snippet 1

Context: `crates/libzkp/src/lib.rs:49` (changes a consensus- or validator-sensitive branch)

Before
```rust
let (pi_hash, metadata, mut u_task) = match task_type {
        x if x == TaskType::Chunk as i32 => {
            let task = serde_json::from_str::<ChunkProvingTask>(task_json)?;
            let (pi_hash, metadata, u_task) =
                gen_universal_chunk_task(task, fork_name.into(), interpreter)?;
            (pi_hash, AnyMetaData::Chunk(metadata), u_task)
        }
        x if x == TaskType::Batch as i32 => {
```
After
```rust
let (pi_hash, metadata, mut u_task) = match task_type {
        x if x == TaskType::Chunk as i32 => {
            let mut task = serde_json::from_str::<ChunkProvingTask>(task_json)?;
            let fork_name = ForkName::from(task.fork_name.to_lowercase().as_str());
            task.fork_name = fork_name.to_string();
            assert_eq!(fork_name_str, task.fork_name.as_str());
            let (pi_hash, metadata, u_task) =
                gen_universal_chunk_task(task, fork_name, interpreter)?;
```

## Snippet 2

Context: `crates/libzkp/src/lib.rs:31` (changes a consensus- or validator-sensitive branch)

Before
```rust
task_type: i32,
    task_json: &str,
    fork_name: &str,
    expected_vk: &[u8],
    interpreter: Option<impl ChunkInterpreter>,
```
After
```rust
task_type: i32,
    task_json: &str,
    fork_name_str: &str,
    expected_vk: &[u8],
    interpreter: Option<impl ChunkInterpreter>,
```

## Snippet 3

Context: `crates/libzkp/src/lib.rs:6` (changes a consensus- or validator-sensitive branch)

Before
```rust
use sbv_primitives::B256;
use scroll_zkvm_types::util::vec_as_base64;
use serde::{Deserialize, Serialize};
use serde_json::value::RawValue;
```
After
```rust
use sbv_primitives::B256;
use scroll_zkvm_types::{public_inputs::ForkName, util::vec_as_base64};
use serde::{Deserialize, Serialize};
use serde_json::value::RawValue;
```

# Fix Pattern

Canonicalize a protocol-relevant selector from structured input and enforce equality with any parallel external representation before continuing into fork-specific processing.

## How It Was Fixed

The fix derives the effective fork from the task payload, normalizes it through `ForkName`, rewrites the task field to canonical text, and adds an `assert_eq!` against the caller-provided fork string before invoking downstream chunk or batch task generation.

# Why It Matters

1. Prevents mismatched fork-name representations from silently flowing into downstream task generation.

2. Removes ambiguity from casing or alias formatting at the task boundary.

3. Makes fork-name disagreement fail immediately instead of being ignored.

4. Supports stronger consistency for fork-specific proving logic, even though exploitability is not established.

# Evidence Notes

The grounded evidence is limited to `crates/libzkp/src/lib.rs`: a new `ForkName` import, parameter rename from `fork_name` to `fork_name_str`, mutable task deserialization, canonicalization of `task.fork_name`, and `assert_eq!(fork_name_str, task.fork_name.as_str())` before downstream calls. Traced context in `crates/libzkp/src/proofs.rs` shows fork-specific PI-hash handling exists, which supports that fork selection matters. However, the patch does not show whether prior behavior could accept invalid proofs, whether task input was attacker-controlled, or whether the bug was only a casing/normalization issue. Protocol security invariant: The fork identifier used when generating a universal proving task should be canonical and should match between the serialized task payload and the separate fork-name argument before downstream fork-specific logic runs. Verification notes: The patch does not prove that mismatched fork names previously led to acceptance of invalid proofs. The evidence does not show whether the bug was exploitable with attacker-controlled task input in production. The patch does not establish impact beyond fork-name inconsistency and canonicalization errors. It is not proven from this diff whether the problematic cases were only casing/alias issues or fully different fork identifiers. No tests are shown in the provided evidence. The diff supports a correctness and consistency fix, but not a confirmed vulnerability. It is not established from the patch whether assertion failure is reachable in production or only guards malformed internal input. The exact impact of a fork mismatch before this change is not demonstrated by the provided code snippets. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-validation`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, input-validation, fork-name, consensus-sensitive`

The patch adds a new invariant check in a fork-sensitive proving path: it canonicalizes the fork name embedded in task JSON, rewrites it to a normalized form, and aborts if it does not match the separately supplied fork-name argument. That is a meaningful hardening change in a security-sensitive blockchain validation/proving context, because it prevents inconsistent fork selection data from silently flowing into downstream fork-specific logic. However, the diff alone does not prove prior exploitability, attacker control, or acceptance of invalid proofs, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `gen_universal_task` now derives `ForkName` from `task.fork_name` instead of trusting only the separate string argument.
2. The patch normalizes fork identity with `ForkName::from(...)` and writes the canonical value back into the task.
3. A new `assert_eq!(fork_name_str, task.fork_name.as_str())` enforces consistency before chunk or batch task generation proceeds.
4. The affected code is fork-specific proving/task-generation logic, and related context shows downstream `pi_hash_check` behavior depends on the selected `ForkName`.

## Missing Evidence

1. No evidence shows that mismatched fork names were attacker-controlled in production.
2. No evidence shows invalid proofs, wrong public inputs, or consensus-invalid state were previously accepted.
3. No tests, issue details, or commit message text explain the concrete failure mode beyond a 'forkname issue'.
4. The patch does not show whether the bug was limited to casing/canonicalization or could select a materially different fork.

## Claim Boundaries

1. Supported claim: the patch hardens fork-name consistency checks in a security-sensitive code path.
2. Supported claim: before the patch, task JSON and the external fork-name parameter could diverge without an explicit equality check here.
3. Not supported: a proven exploitable vulnerability or confirmed acceptance of forged/invalid proofs.
4. Not supported: the original `state-corruption` bug class as a demonstrated impact from the provided diff alone.
