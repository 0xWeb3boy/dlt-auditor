# Root-Cause Card

## Metadata

- ID: `solana-2020-02-26-solana-consensus-242afa7e6b`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-bootstrap-data-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `freshness-and-origin-validation`

## Violated Invariant

- Protocol input must satisfy freshness and origin validation before it can reach RPC method execution, account scan, or transaction forwarding.

## Trust Boundary

- Boundary: untrusted RPC caller to node query/transaction service

## Attack Surface

- Entrypoint type: JSON-RPC request or RPC transaction submission
- Sensitive sink: RPC method execution, account scan, or transaction forwarding

## Root Cause

The likely root cause was that validator bootstrap could accept a genesis package obtained through RPC without a validation boundary tied to configured validator expectations. This is supported by the commit subject and the new config-aware genesis function, but the exact missing check is not visible in the provided snippets.

## Impact Pattern

- Primary impact: consensus-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The evidence supports a likely security fix in Solana validator bootstrap. The commit subject states that genesis config downloaded over RPC is now validated before acceptance, and the snippets show the genesis path changed from a generic ledger download into a dedicated `download_genesis` function that receives `ValidatorConfig`. The exact validation predicate is not shown, so the finding should not claim a proven exploit or concrete consensus split.
