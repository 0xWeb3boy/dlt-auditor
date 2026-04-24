# Root-Cause Card

## Metadata

- ID: `reth-2023-11-29-reth-transaction-processing-2c5a748c5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-malleability`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-signature-enforcement`

## Violated Invariant

- Invariant: When signer recovery is used for normal Ethereum transaction validation, the EIP-2 low-s rule must be enforced so high-s signatures are not treated as canonical; any compatibility path for historical signatures must stay explicitly separate from that checked path.

## Trust Boundary

- Boundary: externally supplied transaction bytes -> signer recovery

## Attack Surface

- Entrypoint type: transaction-signature-decoder
- Sensitive sink: authenticated transaction sender identity

## Impact Pattern

- Primary impact: non-canonical-signature-acceptance
- Secondary impact: signature-validation-bypass

## Short Reusable Lesson

- When signer recovery is used for normal Ethereum transaction validation, the EIP-2 low-s rule must be enforced so high-s signatures are not treated as canonical; any compatibility path for historical signatures must stay explicitly separate from that checked path.
