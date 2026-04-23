# Root-Cause Card

## Metadata

- ID: `go-ethereum-2023-01-11-go-ethereum-transaction-processing-793f0f9ec`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-bounds`

## Violated Invariant

- Invariant: After Shanghai, contract-creation initcode is bounded by params.MaxInitCodeSize and charged additional per-word initcode gas under EIP-3860.

## Trust Boundary

- Boundary: Untrusted transaction data crossing into local execution and admission checks.

## Attack Surface

- Entrypoint type: `transaction validation path`
- Sensitive sink: `canonical-chain selection or persistent chain-state update`

## Impact Pattern

- Primary impact: `resource-exhaustion-mitigation`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch implements EIP-3860 initcode limits and metering for the Shanghai fork.
