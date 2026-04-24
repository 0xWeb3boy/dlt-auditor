# Root-Cause Card

## Metadata

- ID: `geth-arb-2024-04-07-go-ethereum-transaction-processing-ac07554f71`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control-error-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-error-handling`

## Violated Invariant

- Invariant: Authorization predicates must treat successful owner/role lookup as the condition for access and fail closed on lookup errors.

## Trust Boundary

- Boundary: caller cache-management request -> privileged cache/admin operation

## Attack Surface

- Entrypoint type: access-control helper or admin RPC path
- Sensitive sink: privileged cache mutation or chain-owner-only operation

## Impact Pattern

- Primary impact: authorization-bypass-prevention
- Secondary impact: privileged-operation-integrity
- Severity guide: low-medium

## Short Reusable Lesson

- The owner branch in an access predicate accepted the wrong error condition, inverting the success/error handling for chain-owner access. Require both ownership and a nil lookup error before granting access; treat errors as denial.
