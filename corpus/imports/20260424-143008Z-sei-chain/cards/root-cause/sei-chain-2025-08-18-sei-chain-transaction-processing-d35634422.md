# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-08-18-sei-chain-transaction-processing-d35634422`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-legacy-transaction-acceptance`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `legacy-transaction-replay-rejection`

## Violated Invariant

- Invariant: Production transaction admission must reject legacy formats that lack required replay-domain protection.

## Trust Boundary

- Boundary: externally submitted EVM transaction -> signer derivation and execution admission

## Attack Surface

- Entrypoint type: evm-transaction-preprocess
- Sensitive sink: accepting unprotected legacy transaction for execution

## Impact Pattern

- Primary impact: replay-risk
- Secondary impact: authorization-or-identity-integrity

## Short Reusable Lesson

- Reject unsafe legacy transaction formats at preprocessing/admission time, while keeping any compatibility exception behind an explicit test-mode flag. Normal transaction admission no longer accepts the unsafe legacy fallback path. Rejection happens before sender derivation and later transaction handling in the shown paths.
