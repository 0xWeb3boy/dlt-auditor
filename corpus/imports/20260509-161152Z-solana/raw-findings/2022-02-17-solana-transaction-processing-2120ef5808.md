---
case_id: case_20220217_2120ef5808
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2022-02-17
source_refs:
  - git:2120ef580864651f2e16096fd6daaee709cbe3cf
  - "runtime/src/builtins.rs:130"
  - "sdk/src/precompiles.rs:87"
  - "runtime/src/builtins.rs:178"
  - "runtime/src/bank.rs:13288"
bug_class: precompile-lifecycle-hardening
impact_type:
  - security-boundary-hardening
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - precompile
  - feature-gating
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch aligns ed25519 precompile handling with the runtime builtin lifecycle used for precompile program IDs. It adds an `ed25519_program` dummy builtin, changes the ed25519 precompile feature gate to `prevent_calling_precompiles_as_programs`, and adds feature-based removal of the ed25519 builtin. The evidence supports a precompile/runtime feature-gating mismatch, but it does not establish an exploitable vulnerability or a concrete security failure.

## Observed Patch Facts

1. In `runtime/src/builtins.rs`, the patch replaces `/// place holder for secp256k1, remove when the precompile program is deactivated via...` with `Builtin::new(`.

2. In `sdk/src/precompiles.rs`, the patch replaces `Some(ed25519_program_enabled::id()),` with `Some(prevent_calling_precompiles_as_programs::id()),`.

3. In `runtime/src/builtins.rs`, the patch adds `// TODO when feature 'prevent_calling_precompiles_as_programs' is`.

4. In `runtime/src/bank.rs`, the patch replaces `assert_eq!(alive_counts, vec![10, 1, 7]);` with `assert_eq!(alive_counts, vec![11, 1, 7]);`.

## Project Context

The changed code sits primarily in `runtime/src`, `sdk/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sdk/src/ed25519_instruction.rs`, `sdk/src/feature_set.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/ed25519_instruction.rs`, `sdk/src/feature_set.rs`. The strongest project-level identifiers around this patch are `Builtin::new`, `ed25519_program`, `solana_sdk::ed25519_program::id`, and `ActivationType::RemoveProgram`.

## Before/After Behavior

Before the patch, the extracted runtime builtins showed a secp256k1 dummy builtin but no corresponding ed25519 dummy builtin, the ed25519 precompile was gated by `ed25519_program_enabled::id()`, and the shown feature-removal path covered secp256k1 but not ed25519. After the patch, genesis builtins include `ed25519_program` with `dummy_process_instruction`, ed25519 precompile gating uses `prevent_calling_precompiles_as_programs::id()`, and feature builtins remove `ed25519_program` under that same feature. The bank test account-count update is consistent with adding one builtin account.

# Root Cause

The provided evidence indicates inconsistent lifecycle handling for the ed25519 precompile program ID across runtime builtin registration, precompile feature gating, and feature-based builtin removal. It does not prove that this inconsistency allowed forged signatures, replay, unauthorized state mutation, or another concrete exploit.

## Walkthrough

1. The runtime genesis builtin list gains `Builtin::new("ed25519_program", solana_sdk::ed25519_program::id(), dummy_process_instruction)`.

2. The ed25519 entry in `sdk/src/precompiles.rs` changes its feature gate from `ed25519_program_enabled::id()` to `prevent_calling_precompiles_as_programs::id()`.

3. The runtime feature builtin list adds an `ActivationType::RemoveProgram` entry for `ed25519_program` under `prevent_calling_precompiles_as_programs`.

4. The secp256k1 path already shown in the evidence used the same prevent-calling feature pattern, so the patch appears to bring ed25519 into alignment with that lifecycle.

5. The bank test expected alive account count changes from `vec![10, 1, 7]` to `vec![11, 1, 7]`, matching the added builtin account.

6. No provided evidence shows changes to ed25519 signature verification logic or demonstrates a transaction that was improperly accepted before the patch.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/builtins.rs | 130 | registers ed25519_program as a genesis builtin using dummy_process_instruction so ed25519 precompile instructions have a runtime builtin placeholder |
| sdk/src/precompiles.rs | 87 | changes ed25519 precompile gating to the prevent_calling_precompiles_as_programs feature |
| runtime/src/builtins.rs | 178 | adds ed25519_program removal from builtins when prevent_calling_precompiles_as_programs activates |
| runtime/src/bank.rs | 13288 | updates account-count test expectation after ed25519 builtin account is added |

## Code Snippets

## Snippet 1

Context: `runtime/src/builtins.rs:130` (changes a sensitive control or state-update path)

Before
```rust
dummy_process_instruction,
        ),
    ]
}

/// place holder for secp256k1, remove when the precompile program is deactivated via feature activation
fn dummy_process_instruction(
    _first_instruction_account: usize,
```
After
```rust
dummy_process_instruction,
        ),
        Builtin::new(
            "ed25519_program",
            solana_sdk::ed25519_program::id(),
            dummy_process_instruction,
        ),
    ]
```

## Snippet 2

Context: `sdk/src/precompiles.rs:87` (changes a sensitive control or state-update path)

Before
```rust
Precompile::new(
            crate::ed25519_program::id(),
            Some(ed25519_program_enabled::id()),
            crate::ed25519_instruction::verify,
        ),
```
After
```rust
Precompile::new(
            crate::ed25519_program::id(),
            Some(prevent_calling_precompiles_as_programs::id()),
            crate::ed25519_instruction::verify,
        ),
```

## Snippet 3

Context: `runtime/src/builtins.rs:178` (changes a sensitive control or state-update path)

Before
```rust
ActivationType::RemoveProgram,
        ),
        (
            Builtin::new(
```
After
```rust
ActivationType::RemoveProgram,
        ),
        // TODO when feature `prevent_calling_precompiles_as_programs` is
        // cleaned up also remove "ed25519_program" from the main builtins
        // list
        (
            Builtin::new(
                "ed25519_program",
```

## Snippet 4

Context: `runtime/src/bank.rs:13288` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert_eq!(bank2.shrink_candidate_slots(), 0);
        // alive_counts represents the count of alive accounts in the three slots 0,1,2
        assert_eq!(alive_counts, vec![10, 1, 7]);
    }
```
After
```rust
assert_eq!(bank2.shrink_candidate_slots(), 0);
        // alive_counts represents the count of alive accounts in the three slots 0,1,2
        assert_eq!(alive_counts, vec![11, 1, 7]);
    }
```

# Fix Pattern

Align feature gates and runtime registration/removal for a precompile program ID across the SDK precompile table and runtime builtin lifecycle.

## How It Was Fixed

The fix added an ed25519 dummy builtin, switched the ed25519 precompile gate to `prevent_calling_precompiles_as_programs`, added feature-controlled removal of the ed25519 builtin, and updated tests for the added builtin account.

# Why It Matters

1. Consistent feature gating reduces ambiguity in precompile lifecycle behavior.

2. The patch affects runtime exposure and feature activation behavior, not the cryptographic verifier itself.

3. The evidence is compatible with security hardening, but does not establish a vulnerability.

4. The test change supports the registration behavior change rather than an independent guard or validation fix.

# Evidence Notes

Grounded evidence comes from `runtime/src/builtins.rs`, `sdk/src/precompiles.rs`, and the `runtime/src/bank.rs` test baseline change. Unsupported claims removed: signature bypass, replay flaw, attacker-controlled state mutation, validation-before-state-change, and confirmed vulnerability impact. The feature name `prevent_calling_precompiles_as_programs` is security-relevant, but the provided snippets do not prove exploitability or a specific violated security property. Protocol security invariant: Precompile program IDs should have consistent runtime registration, precompile-table gating, and feature-controlled removal behavior so their callable/runtime lifecycle matches the intended feature state. Verification notes: The patch does not show a change to ed25519 signature verification logic. The patch does not prove forged signatures could be accepted before the fix. The patch does not prove replay protection was broken. The patch does not show attacker-controlled state mutation through the dummy builtin handler. The bank.rs change appears to be a test baseline update from adding a builtin account, not an independent runtime guard fix. Confirmed by provided diff snippets only; no external context used. No proof of forged ed25519 signatures being accepted. No proof of replay protection failure. No proof that the dummy builtin handler enabled attacker-controlled state changes. Bank test update appears attributable to an added builtin account. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `precompile-lifecycle-hardening`
Final impact type: `security-boundary-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, precompile, feature-gating, security-hardening`

The patch evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. It aligns ed25519 precompile handling with a feature explicitly named `prevent_calling_precompiles_as_programs`, adds an ed25519 dummy builtin, and removes that builtin under the same prevention feature. That clearly touches exposure and lifecycle control for a signature-related precompile, but the provided evidence does not prove forged signatures, replay, unauthorized state mutation, or a concrete exploit.

## Security Evidence

1. ed25519 precompile gating changes from `ed25519_program_enabled` to `prevent_calling_precompiles_as_programs`.
2. Runtime genesis builtins add `ed25519_program` with `dummy_process_instruction`, matching precompile program lifecycle handling.
3. Feature builtins add `ed25519_program` removal under `prevent_calling_precompiles_as_programs`.
4. The changed subsystem is transaction/runtime handling for a signature precompile program ID.

## Missing Evidence

1. No before/after test demonstrates that calling ed25519 as a normal program was possible or harmful.
2. No evidence shows forged ed25519 signatures being accepted.
3. No evidence shows replay protection failure.
4. No concrete attacker-controlled state mutation or exploit path is shown.

## Claim Boundaries

1. Classify as security hardening rather than a security fix.
2. Do not claim signature validation bypass or replay from this patch alone.
3. Do not claim exploitable impact beyond precompile lifecycle and feature-gating exposure control.
4. The bank account-count test update only supports the added builtin account behavior.
