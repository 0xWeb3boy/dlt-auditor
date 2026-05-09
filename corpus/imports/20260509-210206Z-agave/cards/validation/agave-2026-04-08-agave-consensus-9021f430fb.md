# Validation Card

## Metadata

- ID: `agave-2026-04-08-agave-consensus-9021f430fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`

## What Confirmed The Issue

- Sigverify now compares in_flight_count against verifier.capacity and drops over-capacity packets.
- The service loop passes shared in-flight state through verification and forwarding and records dropped-on-capacity metrics.

## What Could Have Invalidated It

- A bounded channel already prevents capacity overflow before this code.
- Attackers cannot submit enough packets to influence the verifier queue.

## Severity Guidance

- Expected impact band: `remote availability hardening`
- Expected severity band: `medium`
- Rationale: Sigverify is remotely fed and resource-sensitive, but the evidence did not show an actual validator crash, exhaustion reproduction, or consensus impact.

## False-Positive Cautions

- Capacity metrics alone are not a vulnerability unless they gate real work.
- Do not claim invalid-signature acceptance from packet-dropping/backpressure changes.
