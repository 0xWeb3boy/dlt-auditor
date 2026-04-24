# Root-Cause Card

## Metadata

- ID: `optimism-2026-02-12-optimism-transaction-processing-bcec0992d2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-derivation-completeness-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: A disputed post-state should only be handled as a normal transition result if derivation actually reaches the requested disputed L2 block; if derivation stops short, the client should treat that outcome as an invalid transition state instead of reusing the normal success path.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: incorrect-proof-validation
- Secondary impact: state-integrity

## Short Reusable Lesson

- A disputed post-state should only be handled as a normal transition result if derivation actually reaches the requested disputed L2 block; if derivation stops short, the client should treat that outcome as an invalid transition state instead of reusing the normal success path. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
