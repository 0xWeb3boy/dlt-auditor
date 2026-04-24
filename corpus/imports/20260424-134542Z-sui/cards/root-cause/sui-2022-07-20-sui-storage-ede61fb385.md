# Root-Cause Card

## Metadata

- ID: `sui-2022-07-20-sui-storage-ede61fb385`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `authenticated-epoch-storage-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A request crossing a trust boundary must prove the required authority before it can influence privileged protocol state.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: authorizing object access or privileged state mutation

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch appears to add an authenticated/signed epoch storage path and adjust epoch reconfiguration bookkeeping, but the evidence does not establish a vulnerability.
