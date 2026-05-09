# Root-Cause Card

## Metadata

- ID: `solana-2020-05-08-solana-cryptography-f98bfda6f9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `disabled-signature-verification-path`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

Validator-critical code retained development/configuration paths that could replace normal signature verification with disabled verifier implementations. The evidence does not show who could enable those paths or whether invalid packets reached committed state.

## Impact Pattern

- Primary impact: signature-verification-bypass-risk
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The supported finding is security hardening: the patch removes code paths that could disable signature verification in validator vote and shred processing. The evidence supports removal of unsafe bypass configuration, but not a proven remotely exploitable vulnerability or committed-state impact.
