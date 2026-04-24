# Root-Cause Card

## Metadata

- ID: `sui-2024-06-12-sui-staking-116e527a2f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proxy-client-attribution-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The input-validation property must be enforced before untrusted protocol data reaches a security-sensitive sink.

## Trust Boundary

- Boundary: staking transaction or validator metadata -> validator registry

## Attack Surface

- Entrypoint type: staking-registration-or-epoch-transition
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: availability
- Secondary impact: dos-mitigation

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is best described as proxy-aware traffic-control cleanup and hardening, not a confirmed vulnerability fix. The evidence supports that Sui traffic control previously had ambiguous client attribution around socket addresses, connection IP fields, and X-Forwarded-For handling in proxy deployments.
