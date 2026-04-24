# Root-Cause Card

## Metadata

- ID: `sui-2023-01-12-sui-consensus-d5754e7aac`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-commitment`
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

- Primary impact: checkpoint-auditability
- Secondary impact: historical-integrity

## Short Reusable Lesson

- Signature checks are only useful when they bind the exact signer set, message bytes, domain, and epoch consumed by the privileged path. The patch is best treated as checkpoint integrity hardening. It adds user signatures to checkpoint contents because the commit message states checkpoint history otherwise had no record of submitted user signatures after transaction signatures were removed from the TransactionDigest commitment.
