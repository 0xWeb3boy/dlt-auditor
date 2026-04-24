# Root-Cause Card

## Metadata

- ID: `sui-2022-07-04-sui-transaction-processing-362bc47867`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-response-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The input-validation property must be enforced before untrusted protocol data reaches a security-sensitive sink.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: availability
- Secondary impact: protocol-liveness

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch hardens Sui authority sync fetching for checkpoints and finalized cert/effects by carrying known authority sets into aggregator fetch APIs. The evidence supports an availability and strict-response hardening claim, not a proven consensus safety break, invalid-certificate acceptance bug, or asset-loss vulnerability.
