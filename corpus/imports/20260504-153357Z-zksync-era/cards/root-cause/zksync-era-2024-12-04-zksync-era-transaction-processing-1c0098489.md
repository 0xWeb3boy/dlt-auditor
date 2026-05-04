# Root-Cause Card

## Metadata

- ID: `zksync-era-2024-12-04-zksync-era-transaction-processing-1c0098489`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-configuration-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cryptographic-configuration-consistency`

## Violated Invariant

- Invariant: Genesis validation must compare configured verifier key hashes against the exact on-chain verifier function intended for that proof system.

## Trust Boundary

- Boundary: On-chain verifier contract reads cross into local genesis cryptographic configuration.

## Attack Surface

- Entrypoint type: Genesis validation and L1 contract call helper.
- Sensitive sink: Acceptance of verifier verification-key hashes used by proof validation configuration.

## Impact Pattern

- Primary impact: Configuration-integrity hardening for verifier key hashes.
- Secondary impact: Reduced risk of reading the wrong overloaded ABI entry.

## Short Reusable Lesson

- When contract functions are overloaded, cryptographic configuration reads should bind to the exact ABI entry and feed an explicit startup or genesis consistency check.
