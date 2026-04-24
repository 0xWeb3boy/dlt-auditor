# Root-Cause Card

## Metadata

- ID: `sui-2022-06-30-sui-consensus-992af87ebf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `byzantine-availability-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The input-validation property must be enforced before untrusted protocol data reaches a security-sensitive sink.

## Trust Boundary

- Boundary: validator-or-peer message -> consensus state machine

## Attack Surface

- Entrypoint type: consensus-message-handler
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: availability-degradation
- Secondary impact: liveness-degradation

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is best characterized as Byzantine-availability hardening for Sui gossip node sync. It changes transaction/effects download from a direct request to the gossip peer into an AuthorityAggregator-mediated request that can accept one successful authenticated response with timeout handling.
