---
case_id: case_20251124_1210787f39
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
  - git:1210787f39d740b753fbbfb820be10f0bd3d1b02
  - "crates/node/engine/src/attributes.rs:489"
  - "crates/node/engine/src/task_queue/tasks/build/task.rs:111"
  - "crates/protocol/protocol/src/attributes.rs:100"
  - "crates/node/engine/src/attributes.rs:674"
bug_class: payload-derivation-filtering
impact_type:
  - invalid-payload-construction
confidence: medium
tags:
  - blockchain-core
  - consensus
  - payload-derivation
  - transaction-filtering
  - deposit-only
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a protocol-correctness fix in deposit-only payload derivation, not a clearly established security vulnerability. The commit message says deposit-only filtering was incorrect, a new test defines the expected stripping of non-deposit transactions, and the build task now uses `attributes` instead of `inner` when selecting the timestamp and forwarding payload attributes to the engine. The excerpts do not prove exploitability, a live consensus failure, or other concrete security impact.

## Observed Patch Facts

1. In `crates/node/engine/src/attributes.rs`, the patch replaces `attributes.inner.gas_limit = Some(123457);` with `attributes.attributes.gas_limit = Some(123457);`.

2. In `crates/node/engine/src/task_queue/tasks/build/task.rs`, the patch replaces `attributes_envelope.inner.payload_attributes.timestamp,` with `attributes_envelope.attributes.payload_attributes.timestamp,`.

3. In `crates/protocol/protocol/src/attributes.rs`, the patch replaces `assert_eq!(op_attributes_with_parent.inner(), &attributes);` with `assert_eq!(op_attributes_with_parent.attributes(), &attributes);`.

4. In `crates/node/engine/src/attributes.rs`, the patch replaces `let txs = attributes.inner.transactions.as_mut().unwrap();` with `let txs = attributes.attributes.transactions.as_mut().unwrap();`.

## Project Context

The changed code sits primarily in `crates/node/engine/src`, `crates/node/engine`, `crates/node/engine/src/task_queue/tasks/build`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/node/engine/src/client.rs`, `crates/protocol/protocol/src/block.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/node/engine/src/client.rs`, `crates/node/engine/src/task_queue/tasks/task.rs`. The strongest project-level identifiers around this patch are `attributes`, `inner`, `Some`, and `gas_limit`.

## Before/After Behavior

Before the patch, the build path in `crates/node/engine/src/task_queue/tasks/build/task.rs` used `attributes_envelope.inner.payload_attributes.timestamp` and passed `Some(attributes_envelope.inner)` into `fork_choice_updated_v2/v3`. After the patch, it uses `attributes_envelope.attributes.payload_attributes.timestamp` and passes `Some(attributes_envelope.attributes)`. The patch also adds a test in `crates/protocol/protocol/src/attributes.rs` that constructs mixed deposit and non-deposit transaction types and states that `OpAttributesWithParent::as_deposits_only` should strip non-deposit transactions. Related tests in `crates/node/engine/src/attributes.rs` were updated to inspect `attributes.attributes` instead of `attributes.inner`.

# Root Cause

The safest supported root cause is a mismatch between the deposit-only filtering intent and the payload-attributes object actually used downstream. The evidence suggests incorrect field plumbing or inconsistent use of the filtered representation, but the exact faulty implementation of the filter is not shown in the provided excerpts.

## Walkthrough

1. The commit description explicitly says the change fixes payload derivation for Holocene so that deposit-only filtering correctly removes non-deposit payloads.

2. A new test in `crates/protocol/protocol/src/attributes.rs` documents the intended behavior by building `OpPayloadAttributes` with deposit, legacy, and EIP-2930 transactions and asserting deposit-only conversion strips non-deposit types.

3. The build path in `crates/node/engine/src/task_queue/tasks/build/task.rs` changes from using `attributes_envelope.inner` to `attributes_envelope.attributes` for both timestamp selection and the payload attributes submitted to `fork_choice_updated_v2/v3`.

4. Additional test updates in `crates/node/engine/src/attributes.rs` also switch from `inner` to `attributes`, which is consistent with aligning validation and submission around the same payload-attributes container.

5. These excerpts support a derivation/build correctness fix around deposit-only transaction filtering, but they do not by themselves establish a demonstrated security exploit or realized consensus break.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/protocol/protocol/src/attributes.rs | 100 | deposit-only payload attribute handling, including the regression test for stripping non-deposit transactions from `OpAttributesWithParent` |
| crates/node/engine/src/task_queue/tasks/build/task.rs | 84 | engine build path that consumes the selected payload attributes and forwards them to `fork_choice_updated_v2/v3` |
| crates/node/engine/src/attributes.rs | 673 | attribute/block transaction matching test coverage around payload-attribute transaction contents and malformed transaction handling |

## Code Snippets

## Snippet 1

Context: `crates/node/engine/src/attributes.rs:489` (changes a sensitive control or state-update path)

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

Context: `crates/node/engine/src/task_queue/tasks/build/task.rs:111` (changes a consensus- or validator-sensitive branch)

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

Context: `crates/protocol/protocol/src/attributes.rs:100` (changes the branch that decides whether execution stops or continues)

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

Context: `crates/node/engine/src/attributes.rs:674` (changes the branch that decides whether execution stops or continues)

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

Align downstream consumers with the intended filtered payload-attributes object and add regression coverage for the deposit-only filtering invariant.

## How It Was Fixed

The patch adds regression coverage for `OpAttributesWithParent::as_deposits_only` and changes the build task to consume `attributes_envelope.attributes` instead of `attributes_envelope.inner` when choosing the forkchoice version and submitting payload attributes to the engine. Supporting tests were updated to check the same `attributes` container.

# Why It Matters

1. Deposit-only derivation should not include user transaction types.

2. Build logic should consume the same payload-attributes view that the tests validate.

3. The added regression test covers the mixed-transaction case named in the commit message.

# Evidence Notes

The evidence is sufficient to support a transaction-filtering or field-plumbing bug in deposit-only payload derivation. It is not sufficient to support stronger claims such as a proven consensus split, attacker exploitability, fund impact, or a confirmed security incident. Several shown hunks are tests or access-path changes, and the actual implementation diff for the filtering logic is not included in the provided excerpts. Protocol security invariant: When deriving a Holocene deposit-only payload, the `OpPayloadAttributes` used for block building should contain only deposit transactions; non-deposit transactions should be removed before those attributes are forwarded downstream. Verification notes: The patch proves incorrect deposit-only filtering, not an externally demonstrated attacker exploit. The evidence does not show that the bug caused a live consensus split; it shows a protocol-invariant violation in payload construction. Most visible hunks are field-plumbing and tests; the exact pre-fix implementation of the faulty filter is not fully shown. No privilege escalation, theft, or unauthorized state transition is established by this patch alone. No failing pre-patch runtime trace or reproduction was provided. The excerpts do not show the full implementation change for `as_deposits_only` or related derivation code. Security relevance is plausible but not established by the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `payload-derivation-filtering`
Final impact type: `invalid-payload-construction`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, payload-derivation, transaction-filtering, deposit-only`

The patch supports a security-hardening interpretation, not a confirmed security bug. The supplied evidence shows that deposit-only payload derivation could retain non-deposit user transactions and that the build path was changed to forward the filtered `attributes` object into engine forkchoice updates. In a blockchain consensus path, tightening that invariant is security-relevant hardening, but the excerpts do not prove exploitability, a live consensus failure, or a concrete attacker-driven vulnerability.

## Security Evidence

1. The commit message says deposit-only payload derivation was incorrectly filtering non-deposit payloads.
2. A new unit test explicitly asserts that `as_deposits_only` must strip non-deposit transaction types.
3. The build task now uses `attributes_envelope.attributes` instead of `attributes_envelope.inner` when selecting the timestamp and submitting payload attributes to `fork_choice_updated_v2/v3`.
4. The changed path feeds engine forkchoice/build logic, which is consensus-sensitive in a blockchain node.

## Missing Evidence

1. No proof that an attacker could reliably trigger or exploit the pre-fix behavior.
2. No evidence of an observed consensus split, chain halt, or accepted invalid block.
3. The core implementation diff for the faulty filter itself is not shown in the provided excerpts.
4. No demonstrated fund impact, privilege gain, or unauthorized state transition is provided.

## Claim Boundaries

1. The evidence supports tightening a deposit-only payload invariant in a sensitive derivation/build path.
2. The patch does not by itself prove a concrete exploitable vulnerability.
3. The evidence is not strong enough to retain a `consensus-failure` impact label.
4. This should be kept, if at all, as security hardening rather than a confirmed security fix.
