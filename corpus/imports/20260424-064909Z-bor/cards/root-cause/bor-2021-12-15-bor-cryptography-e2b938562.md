# Root-Cause Card

## Metadata

- ID: `bor-2021-12-15-bor-cryptography-e2b938562`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature authorization and domain binding`

## Violated Invariant

- Invariant: A signature or signer action must cover the full security context that gives the message authority, including domain, chain, signer scope, and payload semantics.

## Trust Boundary

- Boundary: untrusted signed payload to verifier or signer boundary

## Attack Surface

- Entrypoint type: transaction/message signature verification path
- Sensitive sink: signer recovery, authorization, or replay-protection decision

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- A fork-unaware canonicalization bug in the Bor seal-hash path caused post-fork signer hashing to omit the BaseFee field that Jaipur-era rules expected.
