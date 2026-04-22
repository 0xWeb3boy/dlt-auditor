# Root-Cause Card

## Metadata

- ID: `base-2026-03-07-base-transaction-processing-37260a7ab`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-signature-validation`

## Violated Invariant

- Invariant: Proof bytes sent on the proposer-to-verifier path should be encoded in one canonical format, with a 65-byte signature and an allowed ECDSA recovery byte value. The provided evidence shows that this invariant is now enforced more explicitly at the encoding boundary, but it does not establish that the prior code violated a security guarantee in an exploitable way.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `malformed-input-rejection`
- Secondary impact: `none`

## Short Reusable Lesson

- Proof bytes sent on the proposer-to-verifier path should be encoded in one canonical format, with a 65-byte signature and an allowed ECDSA recovery byte value. The provided evidence shows that this invariant is now enforced more explicitly at the encoding boundary, but it does not establish that the prior code violated a security guarantee in an exploitable way. The grounded root cause is fragmented proof encoding with incomplete explicit validation at the proposer-side serialization boundary. The evidence only shows that length checks were visible locally before, while `v` validation became explicit after the shared encoder change; it does not show how downstream components handled malformed proof data previously. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
