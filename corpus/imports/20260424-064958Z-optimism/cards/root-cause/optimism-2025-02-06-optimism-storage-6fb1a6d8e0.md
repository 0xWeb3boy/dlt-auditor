# Root-Cause Card

## Metadata

- ID: `optimism-2025-02-06-optimism-storage-6fb1a6d8e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity-binding`

## Violated Invariant

- Invariant: The interop proof client must evaluate the exact disputed transition step. If the agreed pre-state is a SuperRoot and the claimed L2 timestamp does not advance past that pre-state timestamp, the step is a no-op and the claimed post-state must remain the agreed pre-state commitment.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: invalid-claim-acceptance
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- The interop proof client must evaluate the exact disputed transition step. If the agreed pre-state is a SuperRoot and the claimed L2 timestamp does not advance past that pre-state timestamp, the step is a no-op and the claimed post-state must remain the agreed pre-state commitment. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce integrity-binding at the boundary and fail closed before state, privilege, or consensus-visible output changes.
