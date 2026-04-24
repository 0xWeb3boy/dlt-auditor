# Root-Cause Card

## Metadata

- ID: `rippled-2017-11-17-rippled-access-control-a4a43a4de`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `tls-sni-hostname-setup`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trust-root-and-freshness-validation`

## Violated Invariant

- Invariant: Externally supplied trust material must be fetched, redirected, cached, and accepted only under the configured trust roots and transport policy.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: tls-certificate-validation-hardening
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The supplied evidence supports a TLS/SNI setup improvement, not a confirmed vulnerability fix.
