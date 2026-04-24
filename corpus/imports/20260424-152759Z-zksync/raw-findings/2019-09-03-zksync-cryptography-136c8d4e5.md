---
case_id: case_20190903_136c8d4e5
project: zksync
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2019-09-03
source_refs:
  - git:136c8d4e5019593ed5c9b30d4f3cb4831b24a83f
  - "core/storage/src/lib.rs:1442"
  - "core/circuit/src/circuit.rs:1358"
  - "core/circuit/src/circuit.rs:1293"
  - "core/circuit/src/circuit.rs:1653"
bug_class: missing-signature-message-binding
impact_type:
  - integrity
confidence: medium
tags:
  - cryptography
  - zk-circuit
  - signature-validation
  - transaction-binding
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported security-relevant change is in the zk circuit, where the patch constructs serialized transaction bits for transfer_to_new and verifies that those bits match the allocated operation signature-message data. The storage hunk is formatting-only in the supplied evidence and should not contribute to the finding.

## Observed Patch Facts

1. In `core/storage/src/lib.rs`, the patch replaces `return Ok(Err("Could not delete last watched eth block number!".to_string()));` with `return Ok(Err(`.

2. In `core/circuit/src/circuit.rs`, the patch replaces `// construct signature message` with `let is_serialized_tx_correct = verify_signature_message_construction(`.

3. In `core/circuit/src/circuit.rs`, the patch replaces `let pubdata_chunk = select_pubdata_chunk(` with `// construct signature message preimage (serialized_tx)`.

4. In `core/circuit/src/circuit.rs`, the patch replaces `fn allocate_merkle_root<E: JubjubEngine, CS: ConstraintSystem<E>>(` with `fn verify_signature_message_construction<E: JubjubEngine, CS: ConstraintSystem<E>>(`.

## Project Context

The changed code sits primarily in `core/storage/src`, `core/storage`, `core/circuit/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/circuit/src/allocated_structures.rs`, `core/circuit/src/element.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/circuit/src/allocated_structures.rs`, `core/circuit/src/element.rs`. The strongest project-level identifiers around this patch are `serialized_tx_bits`, `CircuitElement::from_fe_strict`, `E::Fr::from_str`, and `E::Fr::CAPACITY`.

## Before/After Behavior

Before the patch, the provided transfer_to_new hunk does not show construction of a canonical signature-message preimage before moving on to pubdata chunk selection, and another path had inline signature-message construction. After the patch, serialized_tx_bits are explicitly built from operation fields, checked through verify_signature_message_construction, and the resulting Boolean is added to lhs_valid_flags.

# Root Cause

The likely root cause was an incomplete or inconsistent circuit constraint tying witness-provided signature-message data to the canonical transaction fields for transfer or transfer_to_new operations. The evidence supports the missing-binding thesis, but does not prove a concrete exploit path or exact pre-patch acceptance condition.

## Walkthrough

1. transfer_to_new builds public data from transaction type, account, token, amount, new pubkey hash, recipient, and fee fields.

2. The patch adds construction of serialized_tx_bits for the signature-message preimage using tx_code 5 and operation fields.

3. A later validity path calls verify_signature_message_construction with serialized_tx_bits and op_data.

4. The returned Boolean is pushed into lhs_valid_flags, making signature-message correctness part of circuit validity.

5. The helper pads and splits the serialized bits and compares them against allocated signature-message representation.

6. The storage change only reformats an existing error return and is not security-relevant based on the supplied before/after.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/circuit/src/circuit.rs | 1271 | transfer_to_new operation constructs public data and canonical signature-message preimage bits |
| core/circuit/src/circuit.rs | 1352 | operation validity flags include verification that serialized transaction bits match allocated operation signature-message data |
| core/circuit/src/circuit.rs | 1653 | helper packs or checks serialized transaction bits against operation signature-message representation |
| core/storage/src/lib.rs | 1439 | formatting-only storage delete error path, not security-relevant in provided evidence |

## Code Snippets

## Snippet 1

Context: `core/storage/src/lib.rs:1442` (changes a sensitive control or state-update path)

Before
```rust
if 0 == deleted {
            error!("Error: could not delete last watched eth block number!");
            return Ok(Err("Could not delete last watched eth block number!".to_string()));
        }
        Ok(Ok(()))
```
After
```rust
if 0 == deleted {
            error!("Error: could not delete last watched eth block number!");
            return Ok(Err(
                "Could not delete last watched eth block number!".to_string()
            ));
        }
        Ok(Ok(()))
```

## Snippet 2

Context: `core/circuit/src/circuit.rs:1358` (changes signature or replay validation logic)

Before
```rust
)?);

        // construct signature message

        let mut serialized_tx_bits = vec![];
        let tx_code = CircuitElement::from_fe_strict(
            cs.namespace(|| "5_ce"),
            || Ok(E::Fr::from_str("5").unwrap()),
```
After
```rust
)?);

        let is_serialized_tx_correct = verify_signature_message_construction(
            cs.namespace(|| "is_serialized_tx_correct"),
            serialized_tx_bits,
            &op_data,
        )?;
```

## Snippet 3

Context: `core/circuit/src/circuit.rs:1293` (changes signature or replay validation logic)

Before
```rust
Boolean::constant(false),
        );
        let pubdata_chunk = select_pubdata_chunk(
            cs.namespace(|| "select_pubdata_chunk"),
```
After
```rust
Boolean::constant(false),
        );

        // construct signature message preimage (serialized_tx)
        let mut serialized_tx_bits = vec![];
        let tx_code = CircuitElement::from_fe_strict(
            cs.namespace(|| "5_ce"),
            || Ok(E::Fr::from_str("5").unwrap()),
```

## Snippet 4

Context: `core/circuit/src/circuit.rs:1653` (changes the branch that decides whether execution stops or continues)

Before
```rust
}
}

fn allocate_merkle_root<E: JubjubEngine, CS: ConstraintSystem<E>>(
    mut cs: CS,
```
After
```rust
}
}
fn verify_signature_message_construction<E: JubjubEngine, CS: ConstraintSystem<E>>(
    mut cs: CS,
    mut serialized_tx_bits: Vec<Boolean>,
    op_data: &AllocatedOperationData<E>,
) -> Result<Boolean, SynthesisError> {
    assert!(serialized_tx_bits.len() < E::Fr::CAPACITY as usize * 2);
```

# Fix Pattern

Construct the canonical signature-message preimage inside the circuit and enforce an explicit validity constraint that binds it to the allocated operation signature-message data.

## How It Was Fixed

The patch adds serialized_tx_bits construction for transfer_to_new, factors signature-message verification into verify_signature_message_construction, and feeds the verification result into the operation validity flags.

# Why It Matters

1. Prevents the proof from accepting a signature message that is not bound to the operation fields.

2. Protects consistency between signed transaction data, public data, and state-transition constraints.

3. A concrete exploit impact such as fund theft or denial of service is not established by the supplied evidence.

# Evidence Notes

Primary support comes from core/circuit/src/circuit.rs around transfer_to_new, the lhs_valid_flags update, and the new verify_signature_message_construction helper. The claim should be limited to likely canonical signature-message binding; the provided evidence does not support panic, malformed-input DoS, storage impact, or a proven exploit. Protocol security invariant: The circuit must constrain the signature message used for verification to the canonical serialized fields of the operation being proven, so the signed message cannot diverge from the transaction fields applied to state and public data. Verification notes: No concrete exploitability is proven by the patch evidence. No denial-of-service or panic-on-malformed-input condition is shown by the provided hunks. The storage change is not security-relevant based on the before/after shown. The exact pre-patch acceptance condition is inferred from the added circuit binding, not fully demonstrated. No evidence is provided that funds could be stolen or signatures forged. No test evidence was supplied. No concrete exploitability proof was supplied. Storage hunk is behavior-preserving formatting in the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-signature-message-binding`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `cryptography, zk-circuit, signature-validation, transaction-binding, security-hardening`

The supplied evidence does not prove a concrete exploitable vulnerability, but it does show a security-sensitive circuit change: canonical serialized transaction bits are constructed and checked against allocated operation signature-message data, and that check is fed into validity flags. This is better retained as security hardening rather than a confirmed security fix. The original liveness-focused metadata is misleading.

## Security Evidence

1. Patch adds canonical signature-message preimage construction for transfer_to_new fields.
2. Patch adds verify_signature_message_construction over serialized_tx_bits and op_data.
3. The result is added to lhs_valid_flags, making signature-message correctness part of circuit validity.
4. Changed code is in zk circuit/signature-message handling, a security-sensitive cryptographic path.

## Missing Evidence

1. No concrete exploit path is shown.
2. No proof is supplied that pre-patch proofs could accept maliciously mismatched transaction fields.
3. No demonstrated fund theft, signature forgery, replay, or denial-of-service impact.
4. No tests, advisory, issue link, or commit message details establish this as a confirmed security fix.

## Claim Boundaries

1. Classify as security hardening, not confirmed vulnerability remediation.
2. Do not claim liveness impact from the supplied evidence.
3. Do not treat the storage formatting hunk as security-relevant.
4. Limit the claim to enforcing consistency between serialized transaction data and signature-message representation in the circuit.
