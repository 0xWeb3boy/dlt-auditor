---
case_id: case_20251124_b2d4a686db
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2025-11-24
source_refs:
  - git:b2d4a686db7b9f0b328f481bd7ba392ecc4c3869
  - "kona/crates/node/engine/src/attributes.rs:489"
  - "kona/crates/node/engine/src/task_queue/tasks/build/task.rs:111"
  - "kona/crates/protocol/protocol/src/attributes.rs:100"
  - "kona/crates/node/engine/src/attributes.rs:674"
bug_class: protocol-invariant-enforcement
impact_type:
  - protocol-integrity-risk
confidence: medium
tags:
  - blockchain-core
  - consensus
  - payload-attributes
  - deposit-only
  - transaction-filtering
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a protocol-correctness fix around deposit-only payload derivation, but it does not fully establish a security vulnerability from the provided excerpts alone. The commit message and added test indicate that non-deposit transactions were not being removed correctly, and the build path was updated to forward the `attributes` field consistently.

## Observed Patch Facts

1. In `kona/crates/node/engine/src/attributes.rs`, the patch replaces `attributes.inner.gas_limit = Some(123457);` with `attributes.attributes.gas_limit = Some(123457);`.

2. In `kona/crates/node/engine/src/task_queue/tasks/build/task.rs`, the patch replaces `attributes_envelope.inner.payload_attributes.timestamp,` with `attributes_envelope.attributes.payload_attributes.timestamp,`.

3. In `kona/crates/protocol/protocol/src/attributes.rs`, the patch replaces `assert_eq!(op_attributes_with_parent.inner(), &attributes);` with `assert_eq!(op_attributes_with_parent.attributes(), &attributes);`.

4. In `kona/crates/node/engine/src/attributes.rs`, the patch replaces `let txs = attributes.inner.transactions.as_mut().unwrap();` with `let txs = attributes.attributes.transactions.as_mut().unwrap();`.

## Project Context

The changed code sits primarily in `kona/crates/node/engine/src`, `kona/crates/node/engine`, `kona/crates/node/engine/src/task_queue/tasks/build`, which anchors the finding in the `consensus` area of the project. Historical context from `kona/crates/node/engine/src/client.rs`, `kona/crates/protocol/protocol/src/block.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `kona/crates/node/engine/src/client.rs`, `kona/crates/node/engine/src/task_queue/tasks/task.rs`. The strongest project-level identifiers around this patch are `attributes`, `inner`, `Some`, and `gas_limit`.

## Before/After Behavior

Before the patch, the commit description says deposit-only filtering of `OpPayloadAttributes` did not correctly remove non-deposit transactions, and the shown build path read from and forwarded `attributes_envelope.inner`. After the patch, a unit test explicitly checks that `as_deposits_only` strips non-deposit transaction types, and `BuildTask::start_build` uses `attributes_envelope.attributes` for timestamp selection and engine submission.

# Root Cause

The visible issue is a logic mismatch between the intended deposit-only filtered attributes and the attributes object actually propagated through the build path. The full buggy implementation is not shown, so the root cause can only be stated as an apparent filtering/propagation error rather than a proven exploitable flaw.

## Walkthrough

1. The commit message states the concrete bug: deposit-only payload derivation was not correctly filtering non-deposit payloads.

2. A new test in `kona/crates/protocol/protocol/src/attributes.rs` exercises `OpAttributesWithParent::as_deposits_only` with mixed transaction types and documents the intended behavior.

3. `kona/crates/node/engine/src/task_queue/tasks/build/task.rs` changes the runtime path from `attributes_envelope.inner` to `attributes_envelope.attributes` when choosing the forkchoice version and sending payload attributes to the engine.

4. Related test updates in `kona/crates/node/engine/src/attributes.rs` also switch from `inner` access to `attributes`, which is consistent with the same wrapper/object alignment.

5. Taken together, the supplied evidence supports a correctness fix for filtered payload propagation, but not a stronger claim about exploitability or demonstrated consensus failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| kona/crates/protocol/protocol/src/attributes.rs | 100 | `OpAttributesWithParent::as_deposits_only` behavior and unit test for stripping non-deposit transactions |
| kona/crates/node/engine/src/task_queue/tasks/build/task.rs | 84 | engine build path that forwards derived payload attributes into `fork_choice_updated_*` |
| kona/crates/node/engine/src/attributes.rs | 673 | attribute/block matching validation around transaction payload contents |

## Code Snippets

## Snippet 1

Context: `kona/crates/node/engine/src/attributes.rs:489` (changes a sensitive control or state-update path)

Before
```rust
let cfg = default_rollup_config();
        let mut attributes = default_attributes();
        attributes.inner.gas_limit = Some(123457);
        let mut block = Block::<Transaction>::default();
        block.header.inner.gas_limit = 123456;
        let check = AttributesMatch::check(cfg, &attributes, &block);
        let expected: AttributesMatch = AttributesMismatch::GasLimit(
            attributes.inner().gas_limit.unwrap_or_default(),
```
After
```rust
let cfg = default_rollup_config();
        let mut attributes = default_attributes();
        attributes.attributes.gas_limit = Some(123457);
        let mut block = Block::<Transaction>::default();
        block.header.inner.gas_limit = 123456;
        let check = AttributesMatch::check(cfg, &attributes, &block);
        let expected: AttributesMatch = AttributesMismatch::GasLimit(
            attributes.attributes().gas_limit.unwrap_or_default(),
```

## Snippet 2

Context: `kona/crates/node/engine/src/task_queue/tasks/build/task.rs:111` (changes a consensus- or validator-sensitive branch)

Before
```rust
let forkchoice_version = EngineForkchoiceVersion::from_cfg(
            &self.cfg,
            attributes_envelope.inner.payload_attributes.timestamp,
        );
        let update = match forkchoice_version {
            EngineForkchoiceVersion::V3 => {
                engine_client
                    .fork_choice_updated_v3(new_forkchoice, Some(attributes_envelope.inner))
```
After
```rust
let forkchoice_version = EngineForkchoiceVersion::from_cfg(
            &self.cfg,
            attributes_envelope.attributes.payload_attributes.timestamp,
        );
        let update = match forkchoice_version {
            EngineForkchoiceVersion::V3 => {
                engine_client
                    .fork_choice_updated_v3(new_forkchoice, Some(attributes_envelope.attributes))
```

## Snippet 3

Context: `kona/crates/protocol/protocol/src/attributes.rs:100` (changes the branch that decides whether execution stops or continues)

Before
```rust
OpAttributesWithParent::new(attributes.clone(), parent, None, is_last_in_span);

        assert_eq!(op_attributes_with_parent.inner(), &attributes);
        assert_eq!(op_attributes_with_parent.parent(), &parent);
        assert_eq!(op_attributes_with_parent.is_last_in_span(), is_last_in_span);
        assert_eq!(op_attributes_with_parent.derived_from(), None);
    }
}
```
After
```rust
OpAttributesWithParent::new(attributes.clone(), parent, None, is_last_in_span);

        assert_eq!(op_attributes_with_parent.attributes(), &attributes);
        assert_eq!(op_attributes_with_parent.parent(), &parent);
        assert_eq!(op_attributes_with_parent.is_last_in_span(), is_last_in_span);
        assert_eq!(op_attributes_with_parent.derived_from(), None);
    }
```

## Snippet 4

Context: `kona/crates/node/engine/src/attributes.rs:674` (changes the branch that decides whether execution stops or continues)

Before
```rust
let cfg = default_rollup_config();
        let (mut attributes, block) = test_transactions_match_helper();
        let txs = attributes.inner.transactions.as_mut().unwrap();
        let first_tx_bytes = txs.first_mut().unwrap();
        *first_tx_bytes = Bytes::copy_from_slice(&[0, 1, 2]);
```
After
```rust
let cfg = default_rollup_config();
        let (mut attributes, block) = test_transactions_match_helper();
        let txs = attributes.attributes.transactions.as_mut().unwrap();
        let first_tx_bytes = txs.first_mut().unwrap();
        *first_tx_bytes = Bytes::copy_from_slice(&[0, 1, 2]);
```

# Fix Pattern

Add a regression test for the intended filtered output, then make downstream runtime code consume the filtered attributes object consistently instead of another wrapper field.

## How It Was Fixed

The patch adds a unit test asserting that deposit-only conversion removes non-deposit transaction encodings, and updates the engine build path to use `attributes_envelope.attributes` when deriving the forkchoice version and forwarding payload attributes to `fork_choice_updated_v2`/`v3`. The observed fix is consistent propagation of the filtered attributes representation.

# Why It Matters

1. Deposit-only derivation rules are protocol-sensitive and should be enforced consistently.

2. Forwarding the wrong attributes object can defeat an earlier filtering step.

3. The evidence shows a real logic fix, but not enough to prove a security incident or exploit path.

# Evidence Notes

The strongest evidence is the commit message, the new `as_deposits_only` unit test, and the runtime `BuildTask::start_build` switch from `inner` to `attributes`. However, the provided excerpts do not include the full pre-patch implementation of `as_deposits_only` or a direct runtime hunk showing the original filtering bug in production code. Because of that gap, claims of confirmed security impact, exploitability, or real-world consensus divergence are not established by the supplied material. Protocol security invariant: A deposit-only payload derivation path should not pass through non-deposit transactions when constructing the payload attributes used by downstream engine logic. Verification notes: The patch does not prove a remotely triggerable exploit path. The evidence does not show whether this affected production networks beyond Holocene-specific behavior. The patch does not prove that consensus divergence occurred in the wild. Some touched hunks are accessor/wrapper updates and tests, so the full runtime root cause is only partially visible from the provided excerpts. The supplied test evidence confirms the intended behavior but not the full pre-patch failure mode in runtime code. The build-path diff shows corrected attribute propagation into engine calls. No provided excerpt demonstrates an attacker-controlled trigger or observed chain impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-invariant-enforcement`
Final impact type: `protocol-integrity-risk`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, payload-attributes, deposit-only, transaction-filtering, hardening`

The patch evidence supports a security-sensitive hardening change in blockchain consensus logic, not a clearly demonstrated exploitable vulnerability. The commit message states that deposit-only payload derivation was incorrectly allowing non-deposit transactions, a new unit test codifies the intended stripping behavior, and the runtime build path is changed to forward `attributes_envelope.attributes` rather than `inner` into engine forkchoice calls. That is enough to retain this as a security-hardening case for a security corpus, but not enough to claim a confirmed security bug or concrete consensus failure from the patch alone.

## Security Evidence

1. Commit message explicitly says deposit-only payload conversion was not correctly filtering non-deposit payloads.
2. New unit test for `OpAttributesWithParent::as_deposits_only` asserts non-deposit transaction types are stripped.
3. `BuildTask::start_build` now derives forkchoice version and submits payload attributes from `attributes_envelope.attributes`, indicating corrected propagation of the filtered payload.
4. The change is in protocol/engine build logic, a security-sensitive consensus path in a blockchain client.

## Missing Evidence

1. No provided hunk shows the full pre-patch implementation of `as_deposits_only` failing in production code.
2. No evidence shows attacker control, exploit steps, or remotely triggerable abuse.
3. No evidence demonstrates real-world consensus divergence, chain split, or funds impact.
4. The excerpts do not fully define the semantic difference between `inner` and `attributes` beyond the observed fix.

## Claim Boundaries

1. Supported claim: the patch hardens enforcement of a deposit-only protocol invariant in a consensus-sensitive path.
2. Not supported: a confirmed exploitable vulnerability or observed security incident.
3. Not supported: definite consensus failure or economic impact on a live network.
