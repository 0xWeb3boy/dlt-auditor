# Root-Cause Card

## Metadata

- ID: `fuel-core-2022-03-02-fuel-core-storage-10a47d0a77`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `block-malleability`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-commitment-binding`

## Violated Invariant

- Block commitments and transaction status records must be derived only after the canonical, fully malleated transaction form and final block identifier are known.

## Trust Boundary

- Boundary: `executor->block-commitment-store`
- Entrypoint type: `state-transition`
- Sensitive sink: `block transaction commitments and persisted transaction status records`

## Attack Surface

- Submit transactions whose final serialized form or witness data differs from the pre-execution representation.
- Observe or depend on transaction status and block commitment outputs.

## Exploit Preconditions

- The execution pipeline computes or persists status/commitment data before all canonical block fields are finalized.
- Consensus or clients rely on those commitments/status records as authoritative.

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `state-integrity`
- Blast radius: `chain-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Do not let execution produce externally visible commitment or status artifacts from provisional transaction or block identity data.
