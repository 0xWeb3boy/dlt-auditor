# Validation Card

## Metadata

- ID: `fuel-core-2025-04-17-fuel-core-storage-103c019fa1`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `missing-utxo-consumption`
- Security verdict: `confirmed`
- Validated as: `security-fix`

## What Confirmed The Issue

- Patch adds DataCoinSigned and DataCoinPredicate to spend_input_utxos handling.
- Regression test checks that a second spend of the same data coin is skipped after commit.

## What Could Have Invalidated It

- Data coins are separately removed in a post-execution finalizer.
- The omitted variants cannot be constructed or accepted on production networks.

## Severity Guidance

- Expected impact band: `critical`
- Expected severity band: `critical`
- Rationale: Confirmed omission in spend-state cleanup can permit repeated spending of the same data coin. Asset integrity impact is critical in UTXO systems.

## False-Positive Cautions

- No issue if data coin inputs are non-spendable metadata only.
- No issue if another storage layer consumes data coins before commit.
