# Root-Cause Card

## Metadata

- ID: `oasis-core-2021-05-24-oasis-core-transaction-processing-25f10e879`
- Bug family: `resource_accounting_and_limits`
- Bug class: `improper-resource-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Txpool admission and batching should enforce configured transaction resource limits using the runtime's checked transaction metadata, not just raw byte length.

## Trust Boundary

- Boundary: `user->mempool`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: `transaction admission and scheduling state`

## Impact Pattern

- Primary impact: `resource-exhaustion`
- Secondary impact: `availability`

## Short Reusable Lesson

- Txpool admission and batching should enforce configured transaction resource limits using the runtime's checked transaction metadata, not just raw byte length. In this pattern, txpool admission logic was still tied to an older raw-byte interface and only the visible size-based check, so configured CheckedTransaction metadata such as per-weight limits was not enforced in that admission path. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
