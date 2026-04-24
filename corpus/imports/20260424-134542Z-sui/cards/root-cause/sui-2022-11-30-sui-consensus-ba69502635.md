# Root-Cause Card

## Metadata

- ID: `sui-2022-11-30-sui-consensus-ba69502635`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-liveness-dos`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: validator-or-peer message -> consensus state machine

## Attack Surface

- Entrypoint type: consensus-message-handler
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: availability

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. This is a confirmed availability/liveness security fix in the checkpoint-consensus path. The commit describes a malicious client delivery pattern where a validator can receive and retain a certificate but never submit it because only a randomized subset of validators was responsible for submission.
