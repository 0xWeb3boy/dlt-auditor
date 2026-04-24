# Root-Cause Card

## Metadata

- ID: `reth-2025-04-25-reth-transaction-processing-82d650594`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: The header-validation path used for block admission should apply the same merge-era header checks consistently. In the shown code, post-Paris Ethereum validation now rejects non-zero difficulty and non-zero nonce in the canonical validator, and the Optimism validator now rejects non-zero nonce in its main path.

## Trust Boundary

- Boundary: block or transaction input -> execution-layer validator

## Attack Surface

- Entrypoint type: transaction/block-validation-path
- Sensitive sink: transaction acceptance or consensus rule application

## Impact Pattern

- Primary impact: invalid-block-acceptance-risk
- Secondary impact: consensus-divergence-risk

## Short Reusable Lesson

- The header-validation path used for block admission should apply the same merge-era header checks consistently. In the shown code, post-Paris Ethereum validation now rejects non-zero difficulty and non-zero nonce in the canonical validator, and the Optimism validator now rejects non-zero nonce in its main path.
