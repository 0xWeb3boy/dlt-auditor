# Root-Cause Card

## Metadata

- ID: `rippled-2025-09-30-rippled-transaction-processing-e1b234cc5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-object-confusion-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-scope-and-domain-binding`

## Violated Invariant

- Invariant: Signed or hashed protocol objects must bind the intended signer, object type, domain, and revocation state before the object is trusted.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: authorization-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch narrows rippled transaction signature-checking helpers so they no longer receive the full PreclaimContext, and it changes multisign branch selection to inspect sigObject rather than ctx.tx.
