# Root-Cause Card

## Metadata

- ID: `avalanchego-2022-11-29-avalanchego-transaction-processing-3511ceac26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-replay-policy-hardening`
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

- The prior helper represented unprotected-transaction policy as a single global boolean, so it could not allow a specific known intentionally unprotected transaction while rejecting other unprotected transactions. The evidence does not show that this caused arbitrary replay acceptance, fund loss, or remote exploitability. ## Walkthrough 1.

## Short Reusable Lesson

- A coarse global unprotected-transaction flag was replaced with a transaction-aware allowlist. The reusable shape is replay-policy code where legacy compatibility should be keyed to exact transaction identity, not a process-wide bypass.
