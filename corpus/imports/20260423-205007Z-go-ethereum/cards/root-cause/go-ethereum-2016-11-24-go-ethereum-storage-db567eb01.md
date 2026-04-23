# Root-Cause Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-db567eb01`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: Ethereum clients must apply EIP158 empty-account touch and snapshot/revert behavior deterministically so consensus-visible state remains compatible across clients and chain history.

## Trust Boundary

- Boundary: Untrusted transaction data crossing into local execution and admission checks.

## Attack Surface

- Entrypoint type: `transaction validation path`
- Sensitive sink: `consensus-visible state transition or journal replay`

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `state-integrity`

## Short Reusable Lesson

- The evidence supports a consensus-relevant StateDB journaling fix, not a broader exploit primitive.
