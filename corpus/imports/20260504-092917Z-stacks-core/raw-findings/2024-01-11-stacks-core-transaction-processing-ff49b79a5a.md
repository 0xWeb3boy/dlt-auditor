---
case_id: case_20240111_ff49b79a5a
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2024-01-11
source_refs:
  - git:ff49b79a5a0c9c39f1f888c76a45faacd57f94e3
  - "stacks-signer/src/runloop.rs:187"
  - "stacks-signer/src/runloop.rs:11"
bug_class: noncanonical-signing-preimage
impact_type:
  - signature-integrity
  - protocol-correctness
tags:
  - validator-ops
  - stacks-signer
  - signature
  - signing-preimage
  - protocol-correctness
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects the message passed into `RunLoopCommand::Sign` after a validated block proposal. The coordinator previously used serialized full block bytes; it now computes `block_validate_ok.block.header.signature_hash()` and signs that digest.

## Observed Patch Facts

1. In `stacks-signer/src/runloop.rs`, the patch replaces `message: block_validate_ok.block.serialize_to_vec(),` with `let signature_hash = block_validate_ok.block.header.signature_hash().expect("BUG: Sta...`.

2. In `stacks-signer/src/runloop.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `stacks-signer/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `stacks-signer/src/lib.rs`, `stacks-signer/src/config.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stacks-signer/src/main.rs`, `stacks-signer/src/client/stacks_client.rs`. The strongest project-level identifiers around this patch are `block`, `RunLoopCommand::Sign`, `signature_hash`, and `stacks_common::codec`. Nearby tests or test-like files include `stacks-signer/src/tests/mod.rs`, `stacks-signer/src/tests/config.rs`.

## Before/After Behavior

Before the patch, `handle_block_validate_response` queued `RunLoopCommand::Sign` with `message: block_validate_ok.block.serialize_to_vec()`. After the patch, it computes the block header `signature_hash()` and queues `RunLoopCommand::Sign` with `message: signature_hash.0.to_vec()`. The removed `StacksMessageCodec` import is consistent with no longer serializing the block in this path.

# Root Cause

The coordinator used a representation-dependent full-block serialization as the signing message instead of the block header's canonical signature hash.

## Walkthrough

1. A validated block proposal reaches `handle_block_validate_response` as `BlockValidateResponse::Ok(block_validate_ok)`.

2. The runloop calculates the coordinator for the current signing round.

3. If the local signer is the coordinator, it queues `RunLoopCommand::Sign`.

4. Before the fix, the queued signing message was `block_validate_ok.block.serialize_to_vec()`.

5. After the fix, the code derives `block_validate_ok.block.header.signature_hash()` and signs `signature_hash.0.to_vec()`.

6. The `expect` documents the invariant that a block already accepted as validated should have a valid signature hash.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-signer/src/runloop.rs | 182 | handles successful block validation responses and decides whether the local signer coordinator starts a signing round |
| stacks-signer/src/runloop.rs | 187 | changed signing message from serialized full block bytes to the block header signature hash |
| testnet/stacks-node/src/tests/signer.rs | 1 | regression coverage referenced by the commit for block written to miners stacker db and signer behavior |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/runloop.rs:187` (changes signature or replay validation logic)

Before
```rust
if coordinator_id == self.signing_round.signer_id {
                    // We are the coordinator. Trigger a signing round for this block
                    self.commands.push_back(RunLoopCommand::Sign {
                        message: block_validate_ok.block.serialize_to_vec(),
                        is_taproot: false,
                        merkle_root: None,
```
After
```rust
if coordinator_id == self.signing_round.signer_id {
                    // We are the coordinator. Trigger a signing round for this block
                    let signature_hash = block_validate_ok.block.header.signature_hash().expect("BUG: Stacks node should never return a validated block with an invalid signature hash");
                    self.commands.push_back(RunLoopCommand::Sign {
                        message: signature_hash.0.to_vec(),
                        is_taproot: false,
                        merkle_root: None,
```

## Snippet 2

Context: `stacks-signer/src/runloop.rs:11` (changes a sensitive control or state-update path)

Before
```rust
use libsigner::{SignerEvent, SignerRunLoop};
use slog::{slog_debug, slog_error, slog_info, slog_warn};
use stacks_common::codec::{read_next, StacksMessageCodec};
use stacks_common::{debug, error, info, warn};
use wsts::common::MerkleRoot;
```
After
```rust
use libsigner::{SignerEvent, SignerRunLoop};
use slog::{slog_debug, slog_error, slog_info, slog_warn};
use stacks_common::codec::read_next;
use stacks_common::{debug, error, info, warn};
use wsts::common::MerkleRoot;
```

# Fix Pattern

Replace the ad hoc serialized signing input with the canonical protocol digest immediately before dispatching the signing command.

## How It Was Fixed

`stacks-signer/src/runloop.rs` now computes the validated block header's `signature_hash()` and passes those bytes to `RunLoopCommand::Sign`. The now-unused `StacksMessageCodec` import was removed.

# Why It Matters

1. Keeps block signing bound to the canonical block header signature hash.

2. Avoids signing serialized full block bytes in this coordinator path.

3. Affects the path that starts signing after successful block validation.

4. Evidence does not prove forgery, replay, theft, or broad consensus failure.

# Evidence Notes

The grounded evidence is the hunk in `stacks-signer/src/runloop.rs`: `message: block_validate_ok.block.serialize_to_vec()` was replaced with computing `block_validate_ok.block.header.signature_hash().expect(...)` and passing `signature_hash.0.to_vec()`. The commit subject also states the signature was fixed to be across the signature hash. The provided evidence does not include the regression test body or downstream signature verification behavior, so broader impact claims should remain bounded. Protocol security invariant: For a validated Nakamoto block proposal, the signer coordinator should initiate signing over the protocol-defined block header signature hash, not over the serialized full block representation. Verification notes: The patch does not prove that attackers could forge valid blocks or signatures. The patch does not prove a replay attack; it only shows the signing preimage was corrected to the signature hash. The patch does not show whether the previous behavior caused invalid signatures, consensus rejection, or a broader safety failure in all deployments. The workflow file change is not security-relevant from the provided evidence. Code evidence supports a signing preimage correction. No evidence was provided showing attacker-controlled exploitation. No evidence was provided proving replay, forgery, theft, or universal consensus failure. Workflow changes are not security-relevant from the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `noncanonical-signing-preimage`
Final impact type: `signature-integrity, protocol-correctness`
Final tags: `validator-ops, stacks-signer, signature, signing-preimage, protocol-correctness`

The supplied patch directly changes a signer coordinator path from signing serialized full block bytes to signing the block header signature hash, matching the commit subject. That is clearly security-sensitive cryptographic/protocol behavior and supports retaining the case as security hardening. The evidence does not prove an exploitable vulnerability, state corruption, replay, forgery, theft, or consensus failure, so security-fix and state-corruption claims are too strong.

## Security Evidence

1. `RunLoopCommand::Sign` message changed from full block serialization to `block.header.signature_hash()` bytes.
2. The changed code runs after successful block validation when the local signer coordinator starts a signing round.
3. The commit subject explicitly says the signature was fixed to be across the signature hash.
4. Removal of `StacksMessageCodec` is consistent with no longer serializing the block for the signing message.

## Missing Evidence

1. No downstream verifier behavior is provided showing the old signatures were accepted, rejected, or exploitable.
2. No regression test body is provided to prove a concrete security failure mode.
3. No evidence shows attacker control, replay, forgery, theft, or broad consensus impact.
4. No protocol specification excerpt is provided proving the exact security invariant beyond the code and commit subject.

## Claim Boundaries

1. Valid claim: the patch corrects the signing preimage to the block header signature hash.
2. Valid claim: the touched path is cryptographic and protocol-sensitive signer behavior.
3. Do not claim proven state corruption or state-integrity compromise from the supplied patch alone.
4. Do not claim a concrete exploitable vulnerability, replay attack, or signature forgery without additional evidence.
