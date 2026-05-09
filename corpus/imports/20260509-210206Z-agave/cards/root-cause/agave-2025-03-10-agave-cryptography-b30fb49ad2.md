# Root-Cause Card

## Metadata

- ID: `agave-2025-03-10-agave-cryptography-b30fb49ad2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-transaction`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `post-removal-control-flow`

## Violated Invariant

- Invariant: After invalid untrusted work is removed from an indexed container, the same iteration must not continue into code that assumes the removed item still exists.

## Trust Boundary

- Boundary: `network-transaction->banking-stage-buffer`

## Attack Surface

- Entrypoint type: `transaction-ingress-buffer`
- Sensitive sink: transaction container lookup guarded by panic-on-missing expect
- Attacker capability: Submit malformed, expired, or otherwise invalid transaction packets.
- Key precondition: The receive-and-buffer loop removes the current transaction id.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `node-availability`
- Severity guidance: `medium` because A panic in transaction ingress can affect validator availability, but the evidence did not prove process-wide termination or network-wide denial of service.

## Short Reusable Lesson

- A packet buffering loop deletes invalid entries from an id-indexed transaction container, then falls through to later code that treats the deleted id as present.
- Structural fix: Add immediate continue/return after removing invalid items so later processing cannot dereference removed container entries.
