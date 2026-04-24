---
case_id: case_20200211_23bdca5c9
project: zksync
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2020-02-11
source_refs:
  - git:23bdca5c939917e2e9a75aea1b97a219b8a9a694
  - "core/circuit/src/witness/change_pubkey_offchain.rs:73"
  - "core/circuit/src/witness/change_pubkey_offchain.rs:146"
  - "core/circuit/src/circuit.rs:1137"
  - "core/circuit/src/circuit.rs:1185"
bug_class: nonce-binding-in-circuit
impact_type:
  - replay-resistance
  - state-transition-integrity
confidence: medium
tags:
  - cryptography
  - zk-circuit
  - nonce-binding
  - state-transition-validation
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch clearly changes the offchain ChangePubKey circuit and witness flow so the transaction nonce is carried into witness data, passed as `OperationArguments.pub_nonce`, emitted through pubdata, and constrained equal to `cur.account.nonce`. This supports a nonce-binding or circuit correctness fix. The provided evidence does not establish an end-to-end vulnerability, replay exploit, signature bypass, unauthorized state transition, or funds-impact scenario, so the security classification should be downgraded to unclear.

## Observed Patch Facts

1. In `core/circuit/src/witness/change_pubkey_offchain.rs`, the patch adds `nonce: Fr::from_str(&change_pubkey_offchain.tx.nonce.to_string()).unwrap(),`.

2. In `core/circuit/src/witness/change_pubkey_offchain.rs`, the patch replaces `pub_nonce: Some(Fr::zero()),` with `pub_nonce: Some(change_pubkey_offcahin.nonce),`.

3. In `core/circuit/src/circuit.rs`, the patch replaces `pubdata_bits.extend(cur.account.nonce.get_bits_be()); //TOKEN_BIT_WIDTH=16` with `pubdata_bits.extend(op_data.pub_nonce.get_bits_be()); //TOKEN_BIT_WIDTH=16`.

4. In `core/circuit/src/circuit.rs`, the patch replaces `let is_valid_first = Boolean::and(` with `let is_pub_nonce_valid = CircuitElement::equals(`.

## Project Context

The changed code sits primarily in `core/circuit/src/witness`, `core/circuit/src`, `core/circuit`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/circuit/src/witness/close_account.rs`, `core/circuit/src/witness/withdraw.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/circuit/src/witness/withdraw.rs`, `core/circuit/src/witness/transfer_to_new.rs`. The strongest project-level identifiers around this patch are `nonce`, `franklin_constants::CHUNK_BIT_WIDTH`, `Some`, and `account`.

## Before/After Behavior

Before the patch, the offchain ChangePubKey witness path omitted the transaction nonce from `ChangePubkeyOffChainData`, passed `Fr::zero()` as `pub_nonce`, and the circuit built pubdata from `cur.account.nonce` directly. The shown circuit validity condition did not include an equality check between an operation-supplied nonce and the current account nonce. After the patch, the witness copies `change_pubkey_offchain.tx.nonce`, passes it as `pub_nonce`, pubdata is built from `op_data.pub_nonce`, and the circuit requires `op_data.pub_nonce == cur.account.nonce` for the first chunk validity path.

# Root Cause

The offchain ChangePubKey circuit path did not consistently carry and constrain the operation nonce as explicit operation data. The witness used a hardcoded zero nonce, while the circuit emitted the account nonce directly in pubdata. Based only on the provided evidence, this is best described as incomplete nonce binding in a newly added circuit operation, not a proven exploitable vulnerability.

## Walkthrough

1. `apply_change_pubkey_offchain_tx` now copies `change_pubkey_offchain.tx.nonce` into `ChangePubkeyOffChainData`.

2. `apply_change_pubkey_offchain` now passes `change_pubkey_offcahin.nonce` as `OperationArguments.pub_nonce` instead of `Fr::zero()`.

3. The circuit now extends pubdata with `op_data.pub_nonce` instead of reading `cur.account.nonce` directly for that field.

4. The circuit adds `is_pub_nonce_valid` comparing `cur.account.nonce` and `op_data.pub_nonce`.

5. The first-chunk validity condition now includes the nonce equality check.

6. The evidence shows a changed circuit acceptance condition, but not a demonstrated attack path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/circuit/src/witness/change_pubkey_offchain.rs | 73 | Copies ChangePubKey transaction nonce into circuit witness data instead of omitting it. |
| core/circuit/src/witness/change_pubkey_offchain.rs | 146 | Passes the actual nonce as OperationArguments.pub_nonce instead of Fr::zero(). |
| core/circuit/src/circuit.rs | 1137 | Builds ChangePubKey offchain pubdata from op_data.pub_nonce rather than directly from current account nonce. |
| core/circuit/src/circuit.rs | 1185 | Adds circuit equality constraint requiring op_data.pub_nonce to equal cur.account.nonce before the first chunk is valid. |

## Code Snippets

## Snippet 1

Context: `core/circuit/src/witness/change_pubkey_offchain.rs:73` (changes signature or replay validation logic)

Before
```rust
address: eth_address_to_fr(&change_pubkey_offchain.tx.account),
        new_pubkey_hash: change_pubkey_offchain.tx.new_pk_hash.to_fr(),
    };
```
After
```rust
address: eth_address_to_fr(&change_pubkey_offchain.tx.account),
        new_pubkey_hash: change_pubkey_offchain.tx.new_pk_hash.to_fr(),
        nonce: Fr::from_str(&change_pubkey_offchain.tx.nonce.to_string()).unwrap(),
    };
```

## Snippet 2

Context: `core/circuit/src/witness/change_pubkey_offchain.rs:146` (changes signature or replay validation logic)

Before
```rust
a: Some(a),
            b: Some(b),
            pub_nonce: Some(Fr::zero()),
            new_pub_key_hash: Some(change_pubkey_offcahin.new_pubkey_hash),
        },
```
After
```rust
a: Some(a),
            b: Some(b),
            pub_nonce: Some(change_pubkey_offcahin.nonce),
            new_pub_key_hash: Some(change_pubkey_offcahin.new_pubkey_hash),
        },
```

## Snippet 3

Context: `core/circuit/src/circuit.rs:1137` (changes signature or replay validation logic)

Before
```rust
pubdata_bits.extend(op_data.eth_address.get_bits_be()); //ETH_KEY_BIT_WIDTH=160
                                                                // NOTE: nonce if verified implicitly here. Current account nonce goes to pubdata and to contract.
        pubdata_bits.extend(cur.account.nonce.get_bits_be()); //TOKEN_BIT_WIDTH=16
        pubdata_bits.resize(
            ChangePubKeyOffchainOp::CHUNKS * franklin_constants::CHUNK_BIT_WIDTH,
            Boolean::constant(false),
        );
```
After
```rust
pubdata_bits.extend(op_data.eth_address.get_bits_be()); //ETH_KEY_BIT_WIDTH=160
                                                                // NOTE: nonce if verified implicitly here. Current account nonce goes to pubdata and to contract.
        pubdata_bits.extend(op_data.pub_nonce.get_bits_be()); //TOKEN_BIT_WIDTH=16
        pubdata_bits.resize(
            ChangePubKeyOp::CHUNKS * franklin_constants::CHUNK_BIT_WIDTH,
            Boolean::constant(false),
        );
```

## Snippet 4

Context: `core/circuit/src/circuit.rs:1185` (changes signature or replay validation logic)

Before
```rust
let tx_valid = multi_and(cs.namespace(|| "is_tx_valid"), &is_valid_flags)?;

        let is_valid_first = Boolean::and(
            cs.namespace(|| "is valid and first"),
            &tx_valid,
            &is_first_chunk,
        )?;
```
After
```rust
let tx_valid = multi_and(cs.namespace(|| "is_tx_valid"), &is_valid_flags)?;

        let is_pub_nonce_valid = CircuitElement::equals(
            cs.namespace(|| "is_pub_nonce_valid"),
            &cur.account.nonce,
            &op_data.pub_nonce,
        )?;
        let is_valid_first = multi_and(
```

# Fix Pattern

Propagate the nonce from transaction data into witness and operation data, emit that same operation nonce in pubdata, and add an in-circuit equality constraint tying it to the current account nonce.

## How It Was Fixed

The patch added the transaction nonce to ChangePubKey offchain witness data, replaced the hardcoded zero `pub_nonce` with the witness nonce, switched pubdata construction to use `op_data.pub_nonce`, and included a circuit equality check between `op_data.pub_nonce` and `cur.account.nonce` in the first-chunk validity condition.

# Why It Matters

1. Nonce handling is security-sensitive in state-transition systems.

2. The patch makes the operation nonce explicit in witness data and pubdata.

3. The circuit now constrains that explicit nonce against account state.

4. No provided evidence proves replay, forgery, theft, or unauthorized state change.

# Evidence Notes

Grounded evidence comes from `core/circuit/src/witness/change_pubkey_offchain.rs` and `core/circuit/src/circuit.rs` in commit `23bdca5c939917e2e9a75aea1b97a219b8a9a694`. The changed lines support a nonce-binding/circuit-correctness finding. Claims about signature forgery, replay exploitation, funds theft, or broader protocol compromise are unsupported by the supplied snippets. The commit subject, `Fix circuit for new op`, is consistent with a correctness fix and does not by itself establish security impact. Protocol security invariant: For the offchain ChangePubKey circuit path, any nonce supplied through operation or witness data and emitted in pubdata should be constrained to match the account nonce used for the proved state transition. Verification notes: No direct exploit path is shown in the provided patch evidence. No proof is provided that signatures could be forged or bypassed. No evidence shows funds theft, unauthorized withdrawal, or state corruption beyond the nonce-binding defect. The classification is limited to the ChangePubKey offchain circuit path, not all transaction types. The commit subject suggests a new-op circuit fix, so this may also be a correctness fix with security impact rather than a known exploited vulnerability. No tests or exploit reproduction were provided. No signature-verification code path was shown. No evidence shows that an invalid transaction could be accepted before the patch. No evidence shows user funds or authorization boundaries were affected. Security relevance is plausible because the changed field is nonce-related, but the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `nonce-binding-in-circuit`
Final impact type: `replay-resistance, state-transition-integrity`
Final confidence: `medium`
Final tags: `cryptography, zk-circuit, nonce-binding, state-transition-validation, hardening`

The patch clearly strengthens a security-sensitive ZK circuit path by propagating the ChangePubKey transaction nonce into witness/operation data and adding an equality constraint requiring it to match the current account nonce. The evidence does not prove an exploitable replay or signature bypass, so it should not be treated as a confirmed security fix, but it is strong enough to keep as security hardening rather than downgrade to unclear.

## Security Evidence

1. Transaction nonce is newly copied into ChangePubkeyOffChainData.
2. OperationArguments.pub_nonce changes from hardcoded Fr::zero() to the transaction-derived nonce.
3. Circuit pubdata is changed to emit op_data.pub_nonce instead of cur.account.nonce directly.
4. Circuit adds is_pub_nonce_valid comparing cur.account.nonce to op_data.pub_nonce and includes it in first-chunk validity.

## Missing Evidence

1. No exploit, test, advisory, or vulnerability description is provided.
2. No signature verification code is shown, so replay or forgery impact is not proven.
3. No evidence shows funds loss, unauthorized withdrawal, or accepted invalid state transition before the patch.

## Claim Boundaries

1. Classify as hardening of nonce binding in the offchain ChangePubKey circuit only.
2. Do not claim a demonstrated replay attack or signature bypass.
3. Do not generalize the issue to all transaction types or broader protocol compromise.
