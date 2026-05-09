# Root-Cause Card

## Metadata

- ID: `agave-2026-04-08-agave-consensus-9021f430fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `in-flight-capacity-accounting`

## Violated Invariant

- Invariant: Asynchronous verification pipelines must account for in-flight work and drop or backpressure new untrusted packets before capacity is exceeded.

## Trust Boundary

- Boundary: `network-packet->sigverify-pipeline`

## Attack Surface

- Entrypoint type: `packet-verification-queue`
- Sensitive sink: sigverify verifier capacity and forwarding pipeline
- Attacker capability: Flood transaction packets toward the verifier pipeline.
- Key precondition: The verifier accepts packets while in-flight count is at or above capacity.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `resource-exhaustion`
- Severity guidance: `medium` because Sigverify is remotely fed and resource-sensitive, but the evidence did not show an actual validator crash, exhaustion reproduction, or consensus impact.

## Short Reusable Lesson

- A packet verification service accepts asynchronous work without a single shared in-flight counter that is checked before enqueueing and updated across verify/send completion.
- Structural fix: Introduce shared in-flight accounting, check capacity before accepting new packets, drop over-capacity packets, and count those drops for observability.
