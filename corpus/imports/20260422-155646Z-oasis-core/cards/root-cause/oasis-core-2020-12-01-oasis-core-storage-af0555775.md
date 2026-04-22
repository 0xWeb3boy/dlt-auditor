# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-12-01-oasis-core-storage-af0555775`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `admission-validation`

## Violated Invariant

- Invariant: Transactions submitted through the Tendermint/ABCI mempool path should undergo normal 'CheckTx' admission validation instead of being accepted via a local bypass mode.

## Trust Boundary

- Boundary: `user->mempool`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: `transaction admission and scheduling state`

## Impact Pattern

- Primary impact: `mempool-validation-bypass`
- Secondary impact: `invalid-transaction-acceptance`

## Short Reusable Lesson

- Transactions submitted through the Tendermint/ABCI mempool path should undergo normal 'CheckTx' admission validation instead of being accepted via a local bypass mode. In this pattern, a debug-only configuration path existed inside the 'CheckTx' admission entrypoint, allowing normal admission validation to be bypassed when locally enabled. The supplied evidence shows that this bypass mechanism was removed, but it does not show that the option was reachable by attackers, used in production, or led to invalid transactions being finalized. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
