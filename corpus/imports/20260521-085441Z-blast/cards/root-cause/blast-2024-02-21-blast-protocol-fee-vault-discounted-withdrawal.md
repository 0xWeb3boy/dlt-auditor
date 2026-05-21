# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-protocol-fee-vault-discounted-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fee-vault-discount-domain-mismatch`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `fee-bucket-discount-exemption`

## Violated Invariant

- Invariant: Protocol fee buckets collected for sequencer/base/L1 cost recovery should not silently share user yield-provider losses unless that policy is explicit.

## Trust Boundary

- Boundary: permissionless L2 fee-vault withdrawal -> L1 discounted ETH settlement

## Attack Surface

- Entrypoint type: FeeVault.withdraw during negative yield
- Sensitive sink: OptimismPortal discounted ETH withdrawal claim

## Impact Pattern

- Primary impact: fee-bypass
- Secondary impact: protocol-revenue-loss

## Short Reusable Lesson

- Protocol fee buckets collected for sequencer/base/L1 cost recovery should not silently share user yield-provider losses unless that policy is explicit. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
