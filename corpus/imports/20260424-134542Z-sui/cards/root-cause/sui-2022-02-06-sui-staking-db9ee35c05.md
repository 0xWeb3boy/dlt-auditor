# Root-Cause Card

## Metadata

- ID: `sui-2022-02-06-sui-staking-db9ee35c05`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `byzantine-authority-robustness`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A request crossing a trust boundary must prove the required authority before it can influence privileged protocol state.

## Trust Boundary

- Boundary: staking transaction or validator metadata -> validator registry

## Attack Surface

- Entrypoint type: staking-registration-or-epoch-transition
- Sensitive sink: authorizing object access or privileged state mutation

## Impact Pattern

- Primary impact: availability
- Secondary impact: sync-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The draft's staking and confirmed vulnerability framing is unsupported. The patch is best described as a FastPay client-authority synchronization robustness and API semantics change: it adds generic authority map/reduce logic, changes ObjectInfoResponse semantics, records deleted-object state in parent_sync, and avoids.
