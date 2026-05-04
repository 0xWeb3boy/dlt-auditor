# Root-Cause Card

## Metadata

- ID: `avalanchego-2026-04-30-avalanchego-p2p-networking-a9c2157265`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-allowlist-admission-gap`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `admission-policy-enforcement`

## Violated Invariant

- Invariant: Every untrusted transaction path into a mempool or txpool must apply the configured admission policy before forwarding the transaction to shared storage or gossip.

## Trust Boundary

- Boundary: RPC or gossip-submitted transactions cross into SAE/Subnet EVM txpool insertion.

## Attack Surface

- Entrypoint type: transaction gossip/mempool add path
- Sensitive sink: txpool acceptance of a transaction that should be blocked by allowlist policy

## Impact Pattern

- Primary impact: access-control, policy-enforcement
- Secondary impact: medium_high_integrity

## Root Cause

- The tx gossip-backed mempool insertion path did not visibly consult an allow-list-aware admission policy before forwarding transactions to txpool.Add. The provided evidence shows the fix adding that missing admission hook, but does not include enough implementation detail to prove the full prior impact beyond mempool admission behavior. ## Walkthrough 1.

## Short Reusable Lesson

- A transaction admission hook was added before forwarding gossip transactions to the txpool. The reusable shape is an allowlist policy enforced in one ingress path but missing from another mempool forwarding path.
