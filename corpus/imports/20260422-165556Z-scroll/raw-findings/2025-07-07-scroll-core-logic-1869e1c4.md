---
case_id: case_20250707_1869e1c4
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
  - git:1869e1c469a5bbfcd88a11ec74db38f076a546c5
  - "crates/libzkp/src/lib.rs:49"
  - "crates/libzkp/src/lib.rs:31"
  - "crates/libzkp/src/lib.rs:6"
bug_class: input-validation
impact_type:
  - protocol-integrity
confidence: medium
tags:
  - blockchain-core
  - core-logic
  - input-validation
  - protocol-consistency
  - fork-binding
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch in `crates/libzkp/src/lib.rs` adds canonicalization and an equality check for `fork_name` when building chunk and batch universal tasks. The code evidence supports a consistency fix at a protocol-sensitive boundary, but it does not establish that this previously enabled invalid proof acceptance, verifier bypass, or another concrete vulnerability.

## Observed Patch Facts

1. In `crates/libzkp/src/lib.rs`, the patch replaces `let task = serde_json::from_str::<ChunkProvingTask>(task_json)?;` with `let mut task = serde_json::from_str::<ChunkProvingTask>(task_json)?;`.

2. In `crates/libzkp/src/lib.rs`, the patch replaces `fork_name: &str,` with `fork_name_str: &str,`.

3. In `crates/libzkp/src/lib.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `crates/libzkp/src`, `crates/libzkp`, which anchors the finding in the `core-logic` area of the project. Historical context from `crates/libzkp/src/tasks.rs`, `crates/libzkp/src/proofs.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/libzkp/src/proofs.rs`, `crates/libzkp/src/tasks/bundle.rs`. The strongest project-level identifiers around this patch are `fork_name`, `task`, `serde_json::from_str`, and `ForkName::from`.

## Before/After Behavior

Before the patch, `gen_universal_task` deserialized chunk and batch tasks and passed the external fork selector downstream, while the task JSON carried its own `fork_name` that was not shown being normalized and checked against that external argument in this entrypoint. After the patch, the function parses `task.fork_name` through `ForkName`, rewrites the task field to the canonical string form, and asserts equality with `fork_name_str` before calling the downstream chunk or batch generator.

# Root Cause

The entrypoint accepted fork information from two representations, the function argument and the deserialized task payload, without first canonicalizing and binding them together in the shown code path.

## Walkthrough

1. `gen_universal_task` changes its parameter name from `fork_name` to `fork_name_str`, separating the raw string input from the canonical enum value used later.

2. The file now imports `scroll_zkvm_types::public_inputs::ForkName`, which supports new fork-name parsing and normalization logic.

3. In the chunk path, the task is made mutable, `task.fork_name` is lowercased and converted with `ForkName::from(...)`, then written back as a canonical string.

4. The new code adds `assert_eq!(fork_name_str, task.fork_name.as_str())` before calling `gen_universal_chunk_task`.

5. The changed-lines list shows the same normalization pattern for the batch path: mutable task, canonicalized fork name, and rewritten task field before generation.

6. A traced downstream function in `crates/libzkp/src/proofs.rs` uses `fork_name` in `pi_hash_by_fork(fork_name)`, which supports that fork choice affects protocol behavior, though not that a security failure previously occurred.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/libzkp/src/lib.rs | 30 | entrypoint that accepts task JSON plus an external fork selector for universal task generation |
| crates/libzkp/src/lib.rs | 49 | chunk and batch task deserialization path where fork name is normalized and checked before generating universal tasks |
| crates/libzkp/src/proofs.rs | 182 | downstream fork-dependent public-input hash check that makes fork/version binding protocol-significant |

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

Canonicalize duplicated protocol-version identifiers at the boundary and reject mismatches before downstream processing.

## How It Was Fixed

The patch adds `ForkName` parsing, converts chunk and batch task deserialization to mutable values, normalizes each task's embedded `fork_name`, writes the canonical value back into the task, and asserts that it matches the separate `fork_name_str` argument before invoking the downstream universal-task generators.

# Why It Matters

1. It removes inconsistent fork representations at a sensitive task-generation boundary.

2. It makes fork-name mismatches fail fast instead of continuing silently.

3. It normalizes case and representation before downstream logic consumes the fork selector.

4. The evidence shows correctness hardening, not a demonstrated exploitable vulnerability.

# Evidence Notes

Supported directly by the diff: new `ForkName` import, mutable deserialization for chunk and batch tasks, canonicalization of `task.fork_name`, rewrite of that field, and `assert_eq!` against the external fork string before generation. Supported by nearby traced context: downstream proof logic uses fork-dependent handling via `pi_hash_by_fork(fork_name)`. Not supported by the provided evidence: prior invalid-proof acceptance, attacker control of the inputs, bundle-path impact, or a concrete exploit scenario. Protocol security invariant: Universal task generation should operate on one canonical fork identifier. The fork name embedded in the task payload and the separately supplied fork selector should be normalized and agree before chunk or batch generation continues. Verification notes: The diff does not prove that an invalid proof could previously be accepted. No attacker-controlled input source for `task_json` or `fork_name_str` is established by the patch alone. The provided evidence does not show whether bundle-task handling had the same issue. The new `assert_eq!` introduces a fail-stop check, but denial-of-service impact is not demonstrated here. The diff is sufficient to show a fork-name consistency check was added. The security impact is not demonstrated by tests, commit message details, or exploit evidence in the provided material. This is better classified as protocol-consistency hardening unless more evidence shows a real acceptance or bypass condition. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-validation`
Final impact type: `protocol-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, core-logic, input-validation, protocol-consistency, fork-binding`

The patch adds canonicalization and an explicit equality check tying the task payload's `fork_name` to the separately supplied fork selector before chunk and batch universal-task generation proceeds. Because downstream proof handling is fork-dependent, this is a meaningful integrity hardening step in a security-sensitive path. However, the provided diff does not prove that the old behavior enabled acceptance of invalid proofs, a verifier bypass, attacker-controlled exploitation, or any concrete security failure, so this fits security hardening rather than a confirmed security bug fix.

## Security Evidence

1. `gen_universal_task` now parses `task.fork_name` through `ForkName`, lowercases it, and rewrites it to a canonical form before use.
2. The new `assert_eq!(fork_name_str, task.fork_name.as_str())` fails fast on mismatched fork identifiers instead of silently continuing.
3. The same normalization pattern is applied in both chunk and batch task paths, indicating deliberate boundary validation.
4. Related context shows fork selection affects downstream proof/public-input handling via `pi_hash_by_fork(fork_name)`, making fork binding security-sensitive.

## Missing Evidence

1. No test, commit message detail, or diff context shows prior acceptance of invalid proofs or malformed tasks.
2. No evidence establishes attacker control over `task_json` or `fork_name_str` in an exposed interface.
3. No proof is provided that consensus divergence, verifier bypass, or state corruption actually occurred before this change.
4. The patch does not show whether other paths such as bundle handling were similarly exposed or exploitable.

## Claim Boundaries

1. Supported claim: the patch hardens a protocol-sensitive boundary by canonicalizing and binding duplicated fork identifiers.
2. Supported claim: mismatched fork names now trigger an immediate failure instead of being tolerated in this entrypoint.
3. Unsupported claim: this commit definitively fixes an exploitable vulnerability or invalid-proof acceptance bug.
4. Unsupported claim: the prior issue caused real consensus failure, state corruption, or a demonstrated verifier bypass.
