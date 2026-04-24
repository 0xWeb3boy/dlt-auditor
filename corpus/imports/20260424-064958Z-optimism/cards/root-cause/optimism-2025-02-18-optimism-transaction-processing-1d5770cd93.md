# Root-Cause Card

## Metadata

- ID: `optimism-2025-02-18-optimism-transaction-processing-1d5770cd93`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-block-hash-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity-binding`

## Violated Invariant

- Invariant: Local verification must reconstruct and validate block data using the exact fork/version-specific fields and rules the protocol expects. The shown patch aligns those rules, but the provided evidence does not establish a vulnerability beyond verification/canonicalization correctness.

## Trust Boundary

- Boundary: RPC/API caller -> node service

## Attack Surface

- Entrypoint type: rpc-handler or API validation path
- Sensitive sink: backend forwarding, access-list approval, or service state derived from caller input

## Impact Pattern

- Primary impact: integrity-validation-bypass
- Secondary impact: state-integrity

## Short Reusable Lesson

- Local verification must reconstruct and validate block data using the exact fork/version-specific fields and rules the protocol expects. The shown patch aligns those rules, but the provided evidence does not establish a vulnerability beyond verification/canonicalization correctness. Similar bugs appear when rpc-handler or API validation path code treats partially checked input as authoritative and lets it reach backend forwarding, access-list approval, or service state derived from caller input. The reusable fix is to enforce integrity-binding at the boundary and fail closed before state, privilege, or consensus-visible output changes.
