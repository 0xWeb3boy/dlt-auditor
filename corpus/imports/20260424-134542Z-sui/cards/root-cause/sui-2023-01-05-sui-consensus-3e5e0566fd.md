# Root-Cause Card

## Metadata

- ID: `sui-2023-01-05-sui-consensus-3e5e0566fd`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-user-signature-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-verification`

## Violated Invariant

- Invariant: A signed protocol object must be accepted only after every required signer, epoch, domain, and payload binding has been checked.

## Trust Boundary

- Boundary: validator-or-peer message -> consensus state machine

## Attack Surface

- Entrypoint type: consensus-message-handler
- Sensitive sink: accepting a signature, certificate, or signed digest as authoritative

## Impact Pattern

- Primary impact: invalid-certificate-acceptance
- Secondary impact: context-dependent

## Short Reusable Lesson

- Signature checks are only useful when they bind the exact signer set, message bytes, domain, and epoch consumed by the privileged path. The patch is likely a security fix for Sui consensus certificate validation. The commit message explicitly says an unresolved deferred guard after unpinning user signatures allowed validators to submit certificates with incorrect user signatures. The supplied code evidence shows new regression support that corrupts `cert.
