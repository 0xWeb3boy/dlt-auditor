# Root-Cause Card

## Metadata

- ID: `reth-2023-07-03-reth-transaction-processing-64554dd0f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: A block body received from an untrusted peer must match the selected header before the downloader assembles a SealedBlock or treats the response as valid; completeness alone is not sufficient, and invalid data should remain attributable to the sending peer.

## Trust Boundary

- Boundary: block or transaction input -> execution-layer validator

## Attack Surface

- Entrypoint type: transaction/block-validation-path
- Sensitive sink: transaction acceptance or consensus rule application

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- A block body received from an untrusted peer must match the selected header before the downloader assembles a SealedBlock or treats the response as valid; completeness alone is not sufficient, and invalid data should remain attributable to the sending peer.
