# Root-Cause Card

## Metadata

- ID: `go-ethereum-2022-12-20-go-ethereum-transaction-processing-b818e73ef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: During The Merge transition, the beacon consensus engine should classify header batches into pre-TTD PoW and post-Merge PoS segments, verify each segment with the appropriate consensus rules, and report errors without assuming the caller already sanitized the headers or blocks.

## Trust Boundary

- Boundary: Untrusted transaction data crossing into local execution and admission checks.

## Attack Surface

- Entrypoint type: `transaction validation path`
- Sensitive sink: `canonical-chain selection or persistent chain-state update`

## Impact Pattern

- Primary impact: `consensus-integrity-hardening`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The provided evidence shows a stricter beacon consensus validation change around The Merge header boundary.
