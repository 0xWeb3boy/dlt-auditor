# Root-Cause Card

## Metadata

- ID: `rippled-2012-05-15-rippled-transaction-processing-9bbbf24f4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-claim-authority-proof`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: authorization-hardening, transaction-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch changes Claim transactions from carrying GeneratorID plus Generator data to carrying Generator, PubKey, and Signature.
