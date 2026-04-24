# Root-Cause Card

## Metadata

- ID: `sui-2024-08-20-sui-consensus-dab9bad618`
- Bug family: `resource_accounting_and_limits`
- Bug class: `consensus-resource-limit-hardening`
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

- Primary impact: resource-exhaustion
- Secondary impact: denial-of-service

## Short Reusable Lesson

- Shared validator resources need bounded accounting and attribution before untrusted work can be amplified. The patch is security-relevant consensus resource-control work, but the provided evidence does not establish a concrete vulnerability or exploit path.
