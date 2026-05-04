# Validation Card

## Metadata

- ID: `moonbeam-2021-02-12-moonbeam-storage-1490dbf7f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `historical-reward-accounting`

## What Confirmed The Issue

- pay_stakers changed from Candidates lookup to round-indexed AtStake snapshot use.
- Patch comments and flow tie the snapshot to reward distribution weighting.

## What Could Have Invalidated It

- Proof that current Candidates was immutable across the reward delay
- An independent settlement ledger that already locked all payout weights before mutation

## Severity Guidance

- Expected impact band: economic_accounting_integrity
- Expected severity band: medium

## False-Positive Cautions

- Live state reads are fine for same-block/current-round rewards
- Snapshots used only for reporting do not imply a payout bug
