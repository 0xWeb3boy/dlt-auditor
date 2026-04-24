# Root-Cause Card

## Metadata

- ID: `sui-2023-02-27-sui-cryptography-d009e82fa3`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-domain-separation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-canonicalization`

## Violated Invariant

- Invariant: A signed protocol object must be accepted only after every required signer, epoch, domain, and payload binding has been checked.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: accepting a signature, certificate, or signed digest as authoritative

## Impact Pattern

- Primary impact: signature-domain-confusion
- Secondary impact: context-dependent

## Short Reusable Lesson

- Signature checks are only useful when they bind the exact signer set, message bytes, domain, and epoch consumed by the privileged path. The patch changes authority signature construction, verification, and batch verification to include an explicit intent scope by signing/verifying serialized `IntentMessage<T>` values.
