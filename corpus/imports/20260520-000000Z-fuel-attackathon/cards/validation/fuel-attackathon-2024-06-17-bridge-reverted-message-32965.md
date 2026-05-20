# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-bridge-reverted-message-32965`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reverted-transaction-withdrawal-message-inclusion`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- Receipts from failed transactions are safe if they are only logs and cannot enter withdrawal commitments.
- No issue if every proof verifier rejects messages from failed transaction status.

## Severity Guidance

- Expected impact band: `critical`
- Expected severity band: `critical`
- Rationale: A failed L2 withdrawal could still produce an L1-withdrawable message while the L2 burn was reverted, threatening bridged funds.

## False-Positive Cautions

- Receipts from failed transactions are safe if they are only logs and cannot enter withdrawal commitments.
- No issue if every proof verifier rejects messages from failed transaction status.
