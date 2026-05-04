# Root-Cause Card

## Metadata

- ID: `zksync-era-2024-09-16-zksync-era-consensus-73c0b7c5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `key-management-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signing-broadcast-separation`

## Violated Invariant

- Invariant: Privileged deployment tooling should allow transaction construction without requiring hot-key signing or immediate broadcast.

## Trust Boundary

- Boundary: Operator transaction-building workflow crosses into private-key custody and L1 broadcast authority.

## Attack Surface

- Entrypoint type: Deployment CLI command.
- Sensitive sink: Privileged L1 deployment transaction signing and broadcasting.

## Impact Pattern

- Primary impact: Reduced exposure of deployment private keys in online tooling.
- Secondary impact: Reduced risk of accidental or premature L1 broadcasts.

## Short Reusable Lesson

- Separate construction, signing, and broadcasting for privileged transactions. Offline or multisig signing support is key-management hardening, not proof by itself that prior key compromise occurred.
