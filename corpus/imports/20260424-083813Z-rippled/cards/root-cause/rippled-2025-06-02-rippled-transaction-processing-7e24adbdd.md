# Root-Cause Card

## Metadata

- ID: `rippled-2025-06-02-rippled-transaction-processing-7e24adbdd`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: privilege-misuse
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch fixes an authorization enforcement gap in NFTokenAcceptOffer::preclaim for non-native issued-asset NFT offer acceptance.
