# Root-Cause Card

## Metadata

- ID: `sui-2024-05-21-sui-storage-d0ebedf217`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-threshold-api-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-verification`

## Violated Invariant

- Invariant: A signed protocol object must be accepted only after every required signer, epoch, domain, and payload binding has been checked.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: accepting a signature, certificate, or signed digest as authoritative

## Impact Pattern

- Primary impact: signature-quorum-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Signature checks are only useful when they bind the exact signer set, message bytes, domain, and epoch consumed by the privileged path. The evidence supports a cleanup or hardening of the bridge committee signature API, not a validated vulnerability fix. Callers no longer pass an explicit threshold to `request_committee_signatures`; the aggregator derives `action.approval_threshold()` internally. Existing shown callers already passed `action.
