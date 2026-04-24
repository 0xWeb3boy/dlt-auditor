# Root-Cause Card

## Metadata

- ID: `rippled-2025-09-10-rippled-transaction-processing-61d628d65`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

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

- The patch tightens delegated-permission validation under the fixDelegateV1_1 amendment. DelegateSet now rejects invalid, unknown, non-delegatable, or amendment-disabled permission values during preflight, and delegated PaymentMint/PaymentBurn checks reject mismatched SendMax and Amount assets.
