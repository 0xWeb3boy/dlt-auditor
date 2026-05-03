# Root-Cause Card

## Metadata

- ID: `firedancer-2024-06-12-firedancer-access-control-8b8649322`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `secret-memory-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `guarded-secret-memory-residency`

## Violated Invariant

- Invariant: Private key material should live in guarded, non-swappable memory and remain isolated from less-trusted child processes and optional sandbox gaps.

## Trust Boundary

- Boundary: Key-loading and runtime sandbox setup crossing into long-lived secret-memory residency.

## Attack Surface

- Entrypoint type: key-loading / signer initialization
- Sensitive sink: private-key memory allocation and sandbox activation

## Impact Pattern

- Primary impact: secret exposure reduction
- Secondary impact: sandbox hardening

## Short Reusable Lesson

- The hardening adds a dedicated protected-memory allocator for key material and surfaces when an optional sandbox layer is unavailable, rather than proving an existing exploit path.
