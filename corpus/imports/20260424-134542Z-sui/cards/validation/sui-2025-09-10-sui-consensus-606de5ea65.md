# Validation Card

## Metadata

- ID: `sui-2025-09-10-sui-consensus-606de5ea65`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-dos-hardening`

## What Confirmed The Issue

- Commit subject and body explicitly describe DoS protection for MFP submitted user transactions.
- Consensus handler adds per-user-transaction digest submission counting gated on mysticeti_fastpath().
- Authority server now derives submitter client address from the request for attribution.
- Consensus submission APIs gain an optional submitter-attribution parameter, with some paths explicitly passing None.

## What Could Have Invalidated It

- No full cache implementation or allowance calculation is shown in the supplied snippets.
- No traffic-controller tally call is included in the provided code evidence.
- No exploit scenario, required volume, or resource exhaustion magnitude is demonstrated.
- No tests proving DoS mitigation behavior are included in the supplied evidence.

## Severity Guidance

- Expected impact band: denial-of-service_or_resource-exhaustion
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Treat as DoS/resource-control hardening rather than a proven vulnerability fix.
- Do not claim serialization, state representation, client-view divergence, or consensus safety was fixed.
- Do not claim signature verification, transaction validity, or cryptographic checks were involved.
- Claims should be scoped to Mysticeti fast path user transaction resubmission accounting.
