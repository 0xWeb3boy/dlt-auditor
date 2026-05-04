# Root-Cause Card

## Metadata

- ID: `avalanchego-2022-11-29-avalanchego-transaction-processing-652572ecf7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection-bypass-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `transaction-scoped-replay-exception`

## Violated Invariant

- Invariant: Replay-protection exceptions must be scoped to explicitly identified transactions rather than enabling all unprotected transactions globally.

## Trust Boundary

- Boundary: Externally submitted EVM transactions cross RPC or mempool admission into transaction validation policy.

## Attack Surface

- Entrypoint type: RPC or backend transaction admission for unprotected EVM transactions
- Sensitive sink: acceptance of an unprotected transaction despite replay-protection policy

## Impact Pattern

- Primary impact: replay-risk-reduction, transaction-policy-integrity
- Secondary impact: medium_or_low_hardening

## Root Cause

- The prior API shape exposed only a coarse backend-wide policy for allowing unprotected transactions. The supplied evidence does not prove this caused unsafe default behavior or an exploitable bypass, but it did not support narrow compatibility exceptions keyed to specific transactions. ## Walkthrough 1. `eth/api_backend.go` changes `UnprotectedAllowed()` into `UnprotectedAllowed(tx *types.Transaction)`. 2.

## Short Reusable Lesson

- A coarse global unprotected-transaction flag was replaced with a transaction-aware allowlist. The reusable shape is replay-policy code where legacy compatibility should be keyed to exact transaction identity, not a process-wide bypass.
