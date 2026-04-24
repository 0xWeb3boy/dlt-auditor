# Root-Cause Card

## Metadata

- ID: `sui-2021-09-01-sui-transaction-processing-779a646e14`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-canonicalization`

## Violated Invariant

- Invariant: A verifier must accept only the canonical signed representation that was bound to the intended signer, domain, and message semantics.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: accepting a signature, certificate, or signed digest as authoritative

## Impact Pattern

- Primary impact: cryptographic-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Signature checks are only useful when they bind the exact signer set, message bytes, domain, and epoch consumed by the privileged path. Commit 779a646e14 changes FastPay signature material from a hand-written Digestible/Sha512 path for Transfer to a Signable/BcsSignable path described as serde plus BCS canonical bytes. It also updates observed signature creation paths to sign value.transfer or certificate.value.transfer.
