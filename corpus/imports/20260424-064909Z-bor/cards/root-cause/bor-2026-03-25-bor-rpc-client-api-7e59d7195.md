# Root-Cause Card

## Metadata

- ID: `bor-2026-03-25-bor-rpc-client-api-7e59d7195`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-input-nondeterminism`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: consensus-divergence
- Secondary impact: state-consistency

## Short Reusable Lesson

- The consensus path selected imported state-sync data using a time-based Heimdall query without first pinning the read to a canonical Heimdall snapshot boundary. Different validators querying different Heimdall views could therefore derive different state-sync sets for the same Bor block.
