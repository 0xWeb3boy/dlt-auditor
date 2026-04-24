# Root-Cause Card

## Metadata

- ID: `sui-2025-09-10-sui-consensus-606de5ea65`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-dos-hardening`
- Confidence tier: `tier_b_likely`

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
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The supported finding is a DoS-oriented hardening change for Sui's Mysticeti fast path transaction submission flow. The patch adds submitted-transaction accounting and client attribution so repeated submissions of the same user transaction digest can be counted after the transaction appears in consensus output and excess.
