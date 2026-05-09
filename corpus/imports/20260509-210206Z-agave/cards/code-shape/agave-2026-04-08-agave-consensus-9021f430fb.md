# Code-Shape Card

## Metadata

- ID: `agave-2026-04-08-agave-consensus-9021f430fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`

## Code Shape Summary

- A packet verification service accepts asynchronous work without a single shared in-flight counter that is checked before enqueueing and updated across verify/send completion.

## Search Motifs

- sigverify in_flight_count leak
- drop packets when verifier capacity reached
- async verifier capacity not checked before receive
- in-flight counter not decremented on send path

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Introduce shared in-flight accounting, check capacity before accepting new packets, drop over-capacity packets, and count those drops for observability.

## False Match Warnings

- The queue is bounded and enforces backpressure before allocation or verification work.
- In-flight accounting is purely metrics and not an admission decision.
- The input source is trusted or rate-limited elsewhere.
