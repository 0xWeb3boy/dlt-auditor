# Validation Card

Record: `omni-cantina-m02-aggvotes-expensive-before-bounds`
Project: `omni-network`
Source finding: `Omni Cantina M-2`

## Positive Confirmation

Confirm AggVote.Verify loops through signatures before verifyAggVotes checks valset.Contains for each claimed signer.

## Preconditions To Confirm

- verifyAggVotes calls AggVote.Verify before valset membership checks.
- A large aggregate fits within CometBFT proposal size.
- Validators must process the proposal before rejecting it.

## False-Positive Cautions

- The expensive operation is bounded by a small count before it runs.
- Membership is rejected before per-signature recovery.
- The data is trusted or locally generated only.

## Minimal Reproduction Or Check

Benchmark a MsgAddVotes containing many valid non-validator signatures and assert recovery occurs before unknown-validator rejection.
