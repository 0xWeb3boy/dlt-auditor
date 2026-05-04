# Root-Cause Card

## Metadata

- ID: `moonbeam-2026-02-21-moonbeam-transaction-processing-05ce4c8c1a`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-protection-policy-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `ethereum-replay-protection-admission-policy`

## Violated Invariant

- Invariant: A production chain should reject legacy Ethereum transactions that lack chain-id replay protection unless an explicit safe policy requires otherwise.

## Trust Boundary

- Boundary: Externally submitted Ethereum transactions cross into node RPC admission and runtime validation.

## Attack Surface

- Entrypoint type: ethereum-transaction-admission
- Sensitive sink: legacy Ethereum transaction acceptance

## Impact Pattern

- Primary impact: request-forgery-or-replay
- Secondary impact: transaction-admission-policy-bypass

## Short Reusable Lesson

- Runtime constants and RPC setup allowed unprotected legacy Ethereum transactions. The patch flips those booleans to false across networks and updates tests away from legacy txs. Disable unprotected transaction acceptance at both runtime configuration and RPC admission boundaries.
