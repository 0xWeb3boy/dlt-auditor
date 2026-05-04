# Validation Card

## Metadata

- ID: `fuel-core-2024-07-27-fuel-core-storage-1cfbb05932`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reverted-transaction-withdrawal-message-inclusion`
- Security verdict: `confirmed`
- Validated as: `security-fix`

## What Confirmed The Issue

- Patch gates message id aggregation with if !reverted.
- Regression tests distinguish successful withdrawal inclusion from reverted transaction exclusion.

## What Could Have Invalidated It

- A separate commitment layer filters reverted receipt message ids before withdrawal proof use.
- The message ids are observability-only and cannot authorize withdrawal or state transitions.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Confirmed bug allowed reverted transactions to affect withdrawal/message commitments. That can threaten asset accounting even if exact theft mechanics depend on downstream checks.

## False-Positive Cautions

- Receipts from reverted transactions may be retained for logs if they are not committed as spendable withdrawal messages.
- No issue if later proof verification rejects any message id from a reverted transaction.
