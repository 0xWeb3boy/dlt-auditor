# Root-Cause Card

## Metadata

- ID: `firedancer-2024-01-17-firedancer-transaction-processing-df9ddc2d1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-isolation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `role-scoped-signing-authorization`

## Violated Invariant

- Invariant: Only explicitly authorized request types may cross into an isolated signing service, and signing keys should stay behind that boundary.

## Trust Boundary

- Boundary: Validator runtime components crossing into the isolated signing/keyguard service.

## Attack Surface

- Entrypoint type: inter-process signing request
- Sensitive sink: validator-key signature generation

## Impact Pattern

- Primary impact: privilege reduction
- Secondary impact: signing boundary hardening

## Short Reusable Lesson

- The hardening introduces a dedicated remote-signing path with role-aware authorization and seccomp isolation so signing requests are mediated instead of implicit.
