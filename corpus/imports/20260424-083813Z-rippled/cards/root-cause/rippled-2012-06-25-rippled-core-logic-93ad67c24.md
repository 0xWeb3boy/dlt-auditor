# Root-Cause Card

## Metadata

- ID: `rippled-2012-06-25-rippled-core-logic-93ad67c24`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `hash-domain-separation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-scope-and-domain-binding`

## Violated Invariant

- Invariant: Signed or hashed protocol objects must bind the intended signer, object type, domain, and revocation state before the object is trusted.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch is likely a security fix for SHAMap node serialization and hash-prefix handling.
