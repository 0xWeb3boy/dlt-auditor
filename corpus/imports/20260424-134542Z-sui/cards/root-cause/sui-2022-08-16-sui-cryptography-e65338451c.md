# Root-Cause Card

## Metadata

- ID: `sui-2022-08-16-sui-cryptography-e65338451c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `empty-batch-signature-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-verification`

## Violated Invariant

- Invariant: A signed protocol object must be accepted only after every required signer, epoch, domain, and payload binding has been checked.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: accepting a signature, certificate, or signed digest as authoritative

## Impact Pattern

- Primary impact: signature-verification-bypass
- Secondary impact: context-dependent

## Short Reusable Lesson

- Signature checks are only useful when they bind the exact signer set, message bytes, domain, and epoch consumed by the privileged path. The patch hardens Narwhal's batch signature verification paths by adding explicit rejection of empty signature batches in the generic `VerifyingKey` default and in Ed25519, BLS12-381, and BLS12-377 implementations.
