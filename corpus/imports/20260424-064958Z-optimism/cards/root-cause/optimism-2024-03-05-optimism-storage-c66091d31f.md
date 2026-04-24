# Root-Cause Card

## Metadata

- ID: `optimism-2024-03-05-optimism-storage-c66091d31f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-domain-separation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separation`

## Violated Invariant

- Invariant: Local dispute-game preimage data should be bound to the challenged L2's identity, so different L2s that share an L1 remain distinguishable.

## Trust Boundary

- Boundary: signed payload -> protocol verifier

## Attack Surface

- Entrypoint type: signature-verification or transaction-decoding path
- Sensitive sink: acceptance of a signature, signer identity, or chain-domain-bound payload

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: signature-or-domain-confusion

## Short Reusable Lesson

- Local dispute-game preimage data should be bound to the challenged L2's identity, so different L2s that share an L1 remain distinguishable. Similar bugs appear when signature-verification or transaction-decoding path code treats partially checked input as authoritative and lets it reach acceptance of a signature, signer identity, or chain-domain-bound payload. The reusable fix is to enforce domain-separation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
