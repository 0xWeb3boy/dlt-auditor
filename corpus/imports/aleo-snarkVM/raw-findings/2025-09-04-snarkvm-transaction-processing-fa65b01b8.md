---
case_id: case_20250904_fa65b01b8
project: snarkvm
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-09-04
source_refs:
  - git:fa65b01b809f25f8a53dec0167250f5eee4f2c5e
  - "synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs:268"
  - "console/algorithms/src/ecdsa/mod.rs:143"
  - "synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs:241"
  - "synthesizer/src/vm/verify.rs:233"
bug_class: cryptographic-input-validation-hardening
impact_type:
  - validation-hardening
  - consensus-integrity-hardening
confidence: medium
tags:
  - blockchain-core
  - ecdsa
  - input-validation
  - consensus-version-gating
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit validation around ECDSA instruction operands, ECDSA verifying-key byte length, and V11 syntax gating before ConsensusVersion::V11. The evidence supports a validation-hardening interpretation, but it does not establish that the prior behavior enabled forged signatures, replay, consensus divergence, or another concrete vulnerability.

## Observed Patch Facts

1. In `synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs`, the patch replaces `// TODO (raychu86): ECDSA - Determine the correct input types based on the variant.` with `// Enforce that the signature is an array of 65 bytes.`.

2. In `console/algorithms/src/ecdsa/mod.rs`, the patch replaces `VerifyingKey::from_sec1_bytes(bytes).map_err(|e| anyhow!("Failed to parse verifying k...` with `// Ensure the byte length is valid.`.

3. In `synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs`, the patch replaces `// TODO (raychu86): ECDSA - Determine if these are the correct input types.` with `// Note: There is no need to check the types here, as this is done in 'output_types'.`.

4. In `synthesizer/src/vm/verify.rs`, the patch replaces `// TODO (raychu86): ECDSA - Uncomment this check when ConsensusVersion::V11 is activa...` with `if consensus_version < ConsensusVersion::V11 {`.

## Project Context

The changed code sits primarily in `synthesizer/program/src/logic/instruction/operation`, `synthesizer/program/src/logic/instruction`, `console/algorithms/src/ecdsa`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `synthesizer/program/src/logic/instruction/operation/sign_verify.rs`, `synthesizer/program/src/logic/instruction/operation/literals.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `synthesizer/program/src/logic/instruction/operation/sign_verify.rs`, `synthesizer/program/src/logic/instruction/operation/literals.rs`. The strongest project-level identifiers around this patch are `ConsensusVersion::V11`, `Self::VERIFYING_KEY_SIZE_IN_BYTES`, `ConsensusVersion`, and `RegisterType::Plaintext`. Nearby tests or test-like files include `synthesizer/src/vm/tests/test_v9.rs`, `synthesizer/src/vm/tests/test_v8.rs`.

## Before/After Behavior

Before the patch, the shown ECDSA output type path had a TODO and returned a boolean output type without the displayed signature operand check; after the patch, it enforces that the first input is a 65-byte u8 array. Before the patch, verifying_key_from_bytes passed byte slices directly to VerifyingKey::from_sec1_bytes; after the patch, it rejects slices with an unexpected length first. Before the patch, the V11 syntax check was commented out in the shown VM deployment verifier; after the patch, deployments containing V11 syntax are rejected when consensus_version is below ConsensusVersion::V11. The finalize path also renames the second loaded operand from ethereum_address to public_key and relies on output_types for validation.

# Root Cause

The shown code had incomplete or inactive validation at ECDSA instruction and deployment admission boundaries. The supplied evidence supports a validation gap, but not a demonstrated security failure mode.

## Walkthrough

1. An ECDSA verification instruction reaches the program validation path with three inputs.

2. Previously, the shown output_types code did not enforce the first operand's ECDSA signature array shape before returning a boolean output type.

3. The patch adds a check that the first input is a plaintext array of u8 with length ECDSASignature::SIGNATURE_SIZE_IN_BYTES.

4. The ECDSA verifying-key parser now rejects byte slices that do not match Self::VERIFYING_KEY_SIZE_IN_BYTES before calling the SEC1 parser.

5. The VM deployment verifier now rejects V11 syntax when the active consensus version is lower than ConsensusVersion::V11.

6. These changes make validation stricter, but the provided evidence does not show that invalid inputs were previously accepted as valid signatures or caused exploitable consensus behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs | 260 | Validates ecdsa_verify input types, including enforcing the first operand as a 65-byte u8 signature array. |
| synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs | 237 | Runtime finalize path loads the already type-checked signature, public key, and message operands for verification. |
| console/algorithms/src/ecdsa/mod.rs | 143 | Rejects ECDSA verifying-key byte slices whose length is not the expected encoded key size before parsing. |
| synthesizer/src/vm/verify.rs | 233 | Rejects deployments containing V11 syntax when consensus_version is below ConsensusVersion::V11. |

## Code Snippets

## Snippet 1

Context: `synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs:268` (changes a sensitive control or state-update path)

Before
```rust
}

        // TODO (raychu86): ECDSA - Determine the correct input types based on the variant.

        Ok(vec![RegisterType::Plaintext(PlaintextType::Literal(LiteralType::Boolean))])
```
After
```rust
}

        // Enforce that the signature is an array of 65 bytes.
        match &input_types[0] {
            RegisterType::Plaintext(PlaintextType::Array(array_type))
                if array_type.base_element_type() == &PlaintextType::Literal(LiteralType::U8)
                    && **array_type.length() as usize == ECDSASignature::SIGNATURE_SIZE_IN_BYTES =>
            {
```

## Snippet 2

Context: `console/algorithms/src/ecdsa/mod.rs:143` (changes signature or replay validation logic)

Before
```rust
/// Parses a verifying key from bytes.
    pub fn verifying_key_from_bytes(bytes: &[u8]) -> Result<VerifyingKey> {
        VerifyingKey::from_sec1_bytes(bytes).map_err(|e| anyhow!("Failed to parse verifying key: {e:?}"))
    }
```
After
```rust
/// Parses a verifying key from bytes.
    pub fn verifying_key_from_bytes(bytes: &[u8]) -> Result<VerifyingKey> {
        // Ensure the byte length is valid.
        if bytes.len() != Self::VERIFYING_KEY_SIZE_IN_BYTES {
            bail!(
                "Invalid ECDSA verifying key length: expected {} bytes, got {} bytes",
                Self::VERIFYING_KEY_SIZE_IN_BYTES,
                bytes.len()
```

## Snippet 3

Context: `synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs:241` (changes signature or replay validation logic)

Before
```rust
}

        // TODO (raychu86): ECDSA - Determine if these are the correct input types.
        // Retrieve the inputs.
        let signature = registers.load(stack, &self.operands[0])?;
        let ethereum_address = registers.load(stack, &self.operands[1])?;
        let message = registers.load(stack, &self.operands[2])?;
```
After
```rust
}

        // Retrieve the inputs.
        // Note: There is no need to check the types here, as this is done in `output_types`.
        let signature = registers.load(stack, &self.operands[0])?;
        let public_key = registers.load(stack, &self.operands[1])?;

        let message = registers.load(stack, &self.operands[2])?;
```

## Snippet 4

Context: `synthesizer/src/vm/verify.rs:233` (changes a consensus- or validator-sensitive branch)

Before
```rust
);
                }
                // TODO (raychu86): ECDSA - Uncomment this check when ConsensusVersion::V11 is activated.
                // if consensus_version <= ConsensusVersion::V10 {
                //     ensure!(
                //         !deployment.program().contains_v11_syntax(),
                //         "Invalid deployment transaction '{id}' - program uses syntax that is not allowed before `ConsensusVersion::V11`"
                //     );
```
After
```rust
);
                }
                if consensus_version < ConsensusVersion::V11 {
                    ensure!(
                        !deployment.program().contains_v11_syntax(),
                        "Invalid deployment transaction '{id}' - program uses syntax that is not allowed before `ConsensusVersion::V11`"
                    );
                }
```

# Fix Pattern

Add explicit admission checks for cryptographic operand encodings and consensus-version-gated syntax before execution or parsing proceeds.

## How It Was Fixed

The patch adds a concrete signature operand type and length check in ecdsa_verify::output_types, adds a verifying-key byte-length check in ECDSASignature::verifying_key_from_bytes, updates finalize to treat operand 1 as public_key, and activates the deployment-time rejection of V11 syntax before ConsensusVersion::V11.

# Why It Matters

1. Malformed ECDSA operands are rejected earlier.

2. Verifying-key parsing now requires the expected encoded length.

3. V11 syntax is gated by the configured consensus version.

4. Exploitability is not established by the supplied evidence.

# Evidence Notes

Grounded evidence comes from changed snippets in synthesizer/program/src/logic/instruction/operation/ecdsa_verify.rs, console/algorithms/src/ecdsa/mod.rs, and synthesizer/src/vm/verify.rs. The evidence does not show a successful bypass, forged verification, replay issue, memory-safety issue, or consensus split. The V11 check may be activation or migration work rather than a vulnerability fix. Protocol security invariant: ECDSA verification instructions and versioned program syntax should be admitted only when their operands and consensus-version constraints match the verifier's expected formats and activation rules. Verification notes: Exploitability is not proven by the patch evidence. No evidence shows that invalid ECDSA operands previously produced a successful forged verification result. No evidence shows replay or nonce-bypass behavior. The ConsensusVersion::V11 change may also be an activation/migration guard, not necessarily a previously exploitable consensus flaw. The exact accepted public-key and message operand types are not fully shown in the provided snippets. Classified as unclear rather than likely because the vulnerability thesis is not proven. Excluded from the security corpus under the provided rules for unestablished security relevance. Downgraded replay/signature-validation claims because no replay or forged-signature behavior is shown. Kept the validation-hardening explanation where directly supported by the diff. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cryptographic-input-validation-hardening`
Final impact type: `validation-hardening, consensus-integrity-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, ecdsa, input-validation, consensus-version-gating, security-hardening`

The patch evidence supports a security-hardening classification: it adds explicit checks for ECDSA signature operand shape, verifying-key byte length, and pre-V11 syntax gating in consensus-version-sensitive validation paths. The evidence does not prove a concrete forged-signature, replay, or consensus-split vulnerability, so it should not be retained as a security-fix, but the tightened cryptographic and consensus admission checks are security-relevant enough for the corpus as hardening.

## Security Evidence

1. Adds enforcement that the ECDSA signature operand is a 65-byte u8 array before returning the boolean output type.
2. Adds explicit verifying-key byte-length validation before parsing SEC1 bytes.
3. Activates rejection of V11 syntax when consensus_version is below ConsensusVersion::V11.
4. Changes are in ECDSA verification and VM deployment verification paths, both security-sensitive in a blockchain core.

## Missing Evidence

1. No evidence that malformed ECDSA operands previously verified successfully.
2. No evidence of replay, request forgery, or signature bypass behavior.
3. No evidence that the inactive V11 syntax gate caused an exploitable consensus split.
4. No advisory, CVE, exploit test, or security-focused commit message is supplied.

## Claim Boundaries

1. Classify as security-hardening, not a proven vulnerability fix.
2. Do not claim forged signatures or replay were possible from this evidence alone.
3. Do not claim consensus divergence was demonstrated.
4. The V11 gating change may overlap with feature activation or migration work, but it still tightens a consensus-sensitive admission check.
