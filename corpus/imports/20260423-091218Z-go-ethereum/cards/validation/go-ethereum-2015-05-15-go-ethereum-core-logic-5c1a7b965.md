# Validation Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-5c1a7b965`
- Bug family: `authz_and_role_gates`
- Bug class: `p2p-sync-validation-bypass`

## What Confirmed The Issue

- Evidence 1: The fix adds a parent-hash queue-membership check before deleting the pending cross-check entry.
- Evidence 2: Regression tests were expanded to build linked fixtures and to exercise made-up chain and block attacks.

## What Could Have Invalidated It

- Compensating control 1: Another pre-existing verifier already ensured that the sampled block's parent belonged to the queued chain.
- Compensating control 2: The sampled response could not influence sync trust or peer acceptance even if it passed the hash-only check.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Keep the claim scoped to downloader sync integrity, not full consensus compromise.
- Caution 2: A hash equality check alone is only security-relevant when the surrounding protocol also depends on chain adjacency.
