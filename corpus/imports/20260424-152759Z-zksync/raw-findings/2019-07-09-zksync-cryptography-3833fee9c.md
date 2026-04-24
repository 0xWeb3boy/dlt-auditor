---
case_id: case_20190709_3833fee9c
project: zksync
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2019-07-09
source_refs:
  - git:3833fee9c22860578d05acafe3133f5e96caa019
  - "src/franklincircuit/src/element.rs:28"
  - "src/franklincircuit/src/circuit.rs:1451"
  - "src/franklincircuit/src/circuit.rs:754"
  - "src/franklincircuit/src/circuit.rs:51"
bug_class: missing-circuit-constraint
impact_type:
  - integrity
  - authorization
confidence: medium
tags:
  - blockchain-core
  - zk-circuit
  - cryptography
  - missing-constraint
  - signature
  - authorization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded security-relevant change is in `src/franklincircuit/src/circuit.rs`, where the transfer validation path adds an equality check between `op_data.signer_pubkey` and `lhs.account.pub_key` and pushes the result into `lhs_valid_flags`. This supports a likely missing-circuit-constraint fix. Claims about panic, malformed-input denial of service, or checked integer conversion are unsupported by the supplied evidence.

## Observed Patch Facts

1. In `src/franklincircuit/src/element.rs`, the patch changes a sensitive implementation path.

2. In `src/franklincircuit/src/circuit.rs`, the patch removes `#[cfg(test)]`.

3. In `src/franklincircuit/src/circuit.rs`, the patch adds `// check signer pubkey`.

4. In `src/franklincircuit/src/circuit.rs`, the patch replaces `let validator_address = CircuitElement::from_fe_padded(cs.namespace(||"validator_addr...` with `let validator_address =`.

## Project Context

The changed code sits primarily in `src/franklincircuit/src`, `src/franklincircuit`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/franklincircuit/src/account.rs`, `src/franklincircuit/src/operation.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/franklincircuit/src/account.rs`, `src/franklincircuit/src/utils.rs`. The strongest project-level identifiers around this patch are `E::Fr`, `namespace`, `CircuitElement::from_fe_padded`, and `validator_address`. Nearby tests or test-like files include `src/franklincircuit/src/tests/transfer.rs`, `src/franklincircuit/src/tests/deposit.rs`.

## Before/After Behavior

Before the patch, the provided transfer-circuit snippet shows `lhs_valid_flags.push(is_first_chunk);` followed by the end of the visible block, with no shown signer-public-key equality check on that path. After the patch, the circuit computes `is_signer_key_correct` with `CircuitPubkey::equals(..., &op_data.signer_pubkey, &lhs.account.pub_key)?` and adds it to `lhs_valid_flags`. The same changed area begins adding operation-argument equality checks. Other shown changes in `element.rs` and validator-address allocation appear to be formatting or context only.

# Root Cause

The transfer validity construction appears to have lacked an explicit constraint tying the signer public key supplied in operation data to the source account public key, at least in the shown path. The evidence does not prove whether other pre-existing constraints mitigated this elsewhere.

## Walkthrough

1. The transfer circuit builds a list of validity flags for the left/source side of the operation.

2. The pre-patch snippet shows the first-chunk flag being pushed, then the visible block ends.

3. The patch adds `is_signer_key_correct` using `CircuitPubkey::equals`.

4. That equality compares `op_data.signer_pubkey` with `lhs.account.pub_key`.

5. The result is pushed into `lhs_valid_flags`, making signer-key agreement part of transfer validity.

6. The changed area also starts checking operation arguments, including an equality involving `op_data.a` and `cur.balance`.

7. The supported finding is a likely missing circuit constraint, not a denial-of-service or panic bug.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/franklincircuit/src/circuit.rs | 754 | adds signer public key equality constraint between operation data and left/source account state |
| src/franklincircuit/src/circuit.rs | 748 | transfer validity flag construction for first chunk and source-side checks |
| src/franklincircuit/src/circuit.rs | 51 | circuit synthesis setup for public data, validator address, and rolling root; shown changes appear mostly formatting/context |
| src/franklincircuit/src/element.rs | 28 | field-element-to-circuit-element helper touched, but provided diff only shows indentation |

## Code Snippets

## Snippet 1

Context: `src/franklincircuit/src/element.rs:28` (changes a sensitive control or state-update path)

Before
```rust
}

      pub fn from_fe_padded<CS: ConstraintSystem<E>, F: FnOnce() -> Result<E::Fr, SynthesisError>>(
        mut cs: CS,
        field_element: F,
```
After
```rust
}

    pub fn from_fe_padded<CS: ConstraintSystem<E>, F: FnOnce() -> Result<E::Fr, SynthesisError>>(
        mut cs: CS,
        field_element: F,
```

## Snippet 2

Context: `src/franklincircuit/src/circuit.rs:1451` (changes signature or replay validation logic)

Before
```rust
.not())
}
#[cfg(test)]
mod test {

    use super::*;

    use franklin_crypto::jubjub::FixedGenerators;
```
After
```rust
.not())
}
```

## Snippet 3

Context: `src/franklincircuit/src/circuit.rs:754` (changes signature or replay validation logic)

Before
```rust
lhs_valid_flags.push(is_first_chunk);

    }
```
After
```rust
lhs_valid_flags.push(is_first_chunk);

        // check signer pubkey
        let is_signer_key_correct = CircuitPubkey::equals(
            cs.namespace(|| "is_signer_key_correct"),
            &op_data.signer_pubkey,
            &lhs.account.pub_key,
        )?;
```

## Snippet 4

Context: `src/franklincircuit/src/circuit.rs:51` (changes a consensus- or validator-sensitive branch)

Before
```rust
public_data_commitment.inputize(cs.namespace(|| "inputize pub_data"))?;

            let validator_address = CircuitElement::from_fe_padded(cs.namespace(||"validator_address"), ||self.validator_address.grab())?;
        

        let mut rolling_root =
            AllocatedNum::alloc(cs.namespace(|| "rolling_root"), || self.old_root.grab())?;
```
After
```rust
public_data_commitment.inputize(cs.namespace(|| "inputize pub_data"))?;

        let validator_address =
            CircuitElement::from_fe_padded(cs.namespace(|| "validator_address"), || {
                self.validator_address.grab()
            })?;

        let mut rolling_root =
```

# Fix Pattern

Add explicit equality constraints to the transfer circuit and include their boolean results in the operation validity flags so witness-provided operation data must match constrained account state.

## How It Was Fixed

The patch adds a `CircuitPubkey::equals` comparison between the operation signer public key and the source account public key, then appends the resulting boolean to `lhs_valid_flags`. It also adds operation-argument equality checks in the same transfer validation area. The supplied evidence does not show the updated test assertions.

# Why It Matters

1. Transfer proofs must bind operation witness data to account state.

2. An unconstrained signer key in operation data would be security-sensitive in a transfer circuit.

3. Validity flags determine whether key transfer constraints are enforced.

4. The evidence supports a missing-constraint thesis, but not a demonstrated exploit.

# Evidence Notes

Strongest evidence: `src/franklincircuit/src/circuit.rs` around lines 748 and 754 shows the added signer public key equality check and inclusion in `lhs_valid_flags`. The evidence does not show the full pre-patch circuit, a concrete exploit, or complete test assertions. The heuristic baseline's panic/liveness claim is unsupported. Changes in `element.rs` and validator-address allocation are not evidence of the vulnerability root cause. Protocol security invariant: A transfer circuit should constrain witness-provided operation data to the committed account state, including requiring the operation signer public key to equal the source account public key and relevant operation arguments to match constrained balances/account fields. Verification notes: The patch evidence does not prove a concrete exploit or successful unauthorized transfer. The evidence does not show the full pre-patch transfer circuit, so other constraints may have partially mitigated the issue. The evidence does not support the heuristic claim about malformed input causing a panic or denial of service. The signature-message construction is marked TODO in the shown code, so this mapping is limited to signer/key and operation-argument constraints. Confirmed from supplied diff snippets only; no external inspection was used. Full pre-patch transfer constraints are not available in the input. No concrete exploit path or failing regression assertion is shown. Classification remains likely rather than confirmed because other constraints may have existed outside the shown snippet. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-circuit-constraint`
Final impact type: `integrity, authorization`
Final confidence: `medium`
Final tags: `blockchain-core, zk-circuit, cryptography, missing-constraint, signature, authorization`

The supplied patch evidence supports a security-relevant tightening in a zk transfer circuit: it adds an explicit equality check requiring the operation signer public key to match the source account public key and includes that result in the validity flags. That is plausibly security hardening for transfer authorization/integrity. However, the evidence does not show the full pre-patch circuit, complete tests, or a concrete exploit, so classifying it as a confirmed security-fix or as a liveness failure would be too strong.

## Security Evidence

1. Patch adds `CircuitPubkey::equals` comparing `op_data.signer_pubkey` with `lhs.account.pub_key`.
2. The result `is_signer_key_correct` is pushed into `lhs_valid_flags`, making the check part of transfer validity.
3. The changed code is in `src/franklincircuit/src/circuit.rs`, a zk circuit implementation path for transfer validation.
4. A missing binding between witness-provided signer data and committed account state is security-sensitive in a transfer circuit.

## Missing Evidence

1. No full pre-patch transfer circuit is provided, so other equivalent constraints cannot be ruled out.
2. No exploit, failing regression assertion, or vulnerability description is shown.
3. The test changes are referenced but not supplied in enough detail to prove the intended security regression.
4. Other shown changes appear to be formatting or test relocation and do not independently support a security claim.

## Claim Boundaries

1. Supported claim: the patch hardens transfer-circuit validity by adding signer-public-key equality constraints.
2. Unsupported claim: a confirmed exploitable unauthorized transfer existed before the patch.
3. Unsupported claim: the issue was a liveness failure, panic, malformed-input denial of service, or checked-conversion bug.
4. Classification should remain likely security-hardening, not confirmed security-fix.
