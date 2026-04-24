# Root-Cause Card

## Metadata

- ID: `optimism-2025-02-06-optimism-storage-ec85a08ef9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-machine-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: When the agreed pre-state is a SuperRoot whose timestamp is at or after the claimed L2 timestamp, the step should be treated as a no-op and the claimed post-state should equal the agreed pre-state commitment; otherwise the transition logic should evaluate the disputed step against the expected post-state commitment.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- When the agreed pre-state is a SuperRoot whose timestamp is at or after the claimed L2 timestamp, the step should be treated as a no-op and the claimed post-state should equal the agreed pre-state commitment; otherwise the transition logic should evaluate the disputed step against the expected post-state commitment. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or.
