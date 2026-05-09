# Root-Cause Card

## Metadata

- ID: `solana-2020-11-13-solana-transaction-processing-5a61827702`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `checked-arithmetic-bounds`

## Violated Invariant

- Protocol input must satisfy checked arithmetic bounds before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

The root cause was overflow-prone accumulator arithmetic in a ledger validation routine. Because the validation decision depended on the accumulated hash count, wrapping could make the checked value differ from the true cumulative count.

## Impact Pattern

- Primary impact: validation-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch fixes overflow-prone arithmetic in Solana ledger entry tick hash verification. `verify_tick_hash_count` previously added each `entry.num_hashes` into a `u64` accumulator with `+=` before checking tick boundaries. The fix uses `saturating_add`, so excessive cumulative hash counts remain excessive instead of wrapping to a smaller value.
