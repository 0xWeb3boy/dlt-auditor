# Root-Cause Card

## Metadata

- ID: `solana-2020-02-26-solana-consensus-87cfac12dd`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `bootstrap-trust-validation`
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

The likely issue was that RPC-fetched genesis data was handled through a generic bootstrap download path without evidence in the provided hunks of a local validator-configuration check before acceptance. The exact missing check is not shown.

## Impact Pattern

- Primary impact: untrusted-bootstrap-state, consensus-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch appears security relevant because the commit subject says it validates a genesis config downloaded over RPC before accepting it, and the code changes move genesis fetching from a generic ledger download path to a genesis-specific path that receives `ValidatorConfig`. However, the provided hunks do not show the actual validation logic, the fields being checked, or a concrete attacker-controlled RPC source, so the vulnerability thesis is not ful...
