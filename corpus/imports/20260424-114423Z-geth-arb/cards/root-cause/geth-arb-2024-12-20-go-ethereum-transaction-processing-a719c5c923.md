# Root-Cause Card

## Metadata

- ID: `geth-arb-2024-12-20-go-ethereum-transaction-processing-a719c5c923`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `hardening-or-correctness-fix`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `round-scoped-admission-binding`

## Violated Invariant

- Invariant: Privileged round-scoped submissions must be validated against the same round tracked by the authoritative state before sequencing continues.

## Trust Boundary

- Boundary: express-lane or privileged submission -> sequencer round admission

## Attack Surface

- Entrypoint type: sequencer privileged submission handler
- Sensitive sink: round-specific sequencing or express-lane acceptance

## Impact Pattern

- Primary impact: sequencer-integrity
- Secondary impact: authorization-freshness
- Severity guide: medium

## Short Reusable Lesson

- The sequencer admission loop needed to keep processing only while the authoritative round still matched the submitted message round. Add the round equality condition to the processing loop so stale or cross-round messages stop before sequencing.
