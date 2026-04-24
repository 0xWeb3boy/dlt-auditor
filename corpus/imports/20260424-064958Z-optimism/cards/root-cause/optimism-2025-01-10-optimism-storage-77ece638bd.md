# Root-Cause Card

## Metadata

- ID: `optimism-2025-01-10-optimism-storage-77ece638bd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: When the supervisor validates an executing message against stored logs, the returned inclusion context should correspond to the exact sealed block expected by the protocol, including the expected timestamp, rather than only matching block number, log index, and log hash.

## Trust Boundary

- Boundary: artifact/archive input -> host filesystem

## Attack Surface

- Entrypoint type: archive-extraction or file-materialization path
- Sensitive sink: filesystem write outside the intended extraction or artifact directory

## Impact Pattern

- Primary impact: protocol-integrity
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- When the supervisor validates an executing message against stored logs, the returned inclusion context should correspond to the exact sealed block expected by the protocol, including the expected timestamp, rather than only matching block number, log index, and log hash. Similar bugs appear when archive-extraction or file-materialization path code treats partially checked input as authoritative and lets it reach filesystem write outside the intended extraction or artifact directory. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
