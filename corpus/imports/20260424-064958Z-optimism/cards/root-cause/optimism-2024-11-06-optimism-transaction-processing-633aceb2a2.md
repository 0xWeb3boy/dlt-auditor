# Root-Cause Card

## Metadata

- ID: `optimism-2024-11-06-optimism-transaction-processing-633aceb2a2`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-metadata-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-and-context-binding`

## Violated Invariant

- Invariant: The evidence points to a correctness invariant around legacy transaction reconstruction: y-parity, protected-state, and chain_id should stay coherent with EIP-155 semantics. The provided material does not establish that this invariant failure was exploitable as a security vulnerability in this project.

## Trust Boundary

- Boundary: signed payload -> protocol verifier

## Attack Surface

- Entrypoint type: signature-verification or transaction-decoding path
- Sensitive sink: acceptance of a signature, signer identity, or chain-domain-bound payload

## Impact Pattern

- Primary impact: replay-protection-risk
- Secondary impact: input-validation-risk

## Short Reusable Lesson

- The evidence points to a correctness invariant around legacy transaction reconstruction: y-parity, protected-state, and chain_id should stay coherent with EIP-155 semantics. The provided material does not establish that this invariant failure was exploitable as a security vulnerability in this project. Similar bugs appear when signature-verification or transaction-decoding path code treats partially checked input as authoritative and lets it reach acceptance of a signature, signer identity, or chain-domain-bound payload. The reusable fix is to enforce signer-and-context-binding at the boundary and fail closed before state, privilege, or.
