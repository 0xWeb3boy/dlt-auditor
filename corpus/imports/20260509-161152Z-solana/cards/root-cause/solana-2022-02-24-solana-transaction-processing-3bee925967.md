# Root-Cause Card

## Metadata

- ID: `solana-2022-02-24-solana-transaction-processing-3bee925967`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-resource-accounting-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The old rent-state transition rule was too coarse: it tracked the rent-paying classification but not the data size associated with that classification. That left resized rent-paying accounts outside the intended rent-exemption requirement shown by the patch comment and commit subject.

## Impact Pattern

- Primary impact: resource-accounting-invariant
- Expected band: availability_or_resource_exhaustion
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch likely fixes a Solana runtime rent-validation invariant gap. The strongest evidence is the change to `RentState::transition_allowed_from`, which adds realloc-aware comparison of pre- and post-transaction `RentPaying` data sizes and rejects rent-paying-to-rent-paying transitions when the size changed.
