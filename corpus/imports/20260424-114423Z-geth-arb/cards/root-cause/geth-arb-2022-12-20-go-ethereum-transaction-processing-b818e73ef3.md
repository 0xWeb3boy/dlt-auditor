# Root-Cause Card

## Metadata

- ID: `geth-arb-2022-12-20-go-ethereum-transaction-processing-b818e73ef3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-boundary-consensus-validation`

## Violated Invariant

- Invariant: Fork-boundary consensus checks must validate the exact transition conditions for mixed pre-fork and post-fork batches before accepting headers as valid.

## Trust Boundary

- Boundary: peer-supplied header batch -> consensus header verification

## Attack Surface

- Entrypoint type: header verifier or beacon/merge transition checker
- Sensitive sink: header validity result and invalid-header cache

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: header-validation-integrity
- Severity guide: medium

## Short Reusable Lesson

- Header verification needed explicit handling for mixed proof-of-work/proof-of-stake or merge-boundary batches so terminal difficulty and per-header errors were correct. Split verification at the fork boundary, validate terminal total difficulty explicitly, and cache or report invalid transition headers precisely.
