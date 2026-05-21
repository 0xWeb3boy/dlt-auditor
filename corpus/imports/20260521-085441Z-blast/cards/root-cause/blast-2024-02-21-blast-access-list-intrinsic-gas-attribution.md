# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-access-list-intrinsic-gas-attribution`
- Bug family: `resource_accounting_and_limits`
- Bug class: `intrinsic-gas-attribution-mismatch`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `fee-recipient-attribution`

## Violated Invariant

- Invariant: Access-list intrinsic gas paid to warm contract/storage accesses should be attributed to the contract or surface that benefits from the warmed access, not a global bucket.

## Trust Boundary

- Boundary: transaction intrinsic gas -> developer gas accounting

## Attack Surface

- Entrypoint type: EIP-2930 access list transaction
- Sensitive sink: GasTracker allocation and claimable gas recipient

## Impact Pattern

- Primary impact: fee-attribution-error
- Secondary impact: fee-bypass

## Short Reusable Lesson

- Access-list intrinsic gas paid to warm contract/storage accesses should be attributed to the contract or surface that benefits from the warmed access, not a global bucket. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
