# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m08-rebasing-token-escrow-drift`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `rebasing-token-escrow-supply-drift`

## What Confirmed The Issue

- Public C4 report section M-08 rated this as Medium.
- The report kept this as a non-low finding without a confirmed mitigation PR in the included mitigation scope.

## What Could Have Invalidated It

- No issue if rebasing tokens are explicitly unsupported and blocked.
- No issue if conversion uses shares or regularly reconciles escrow balance changes.

## Severity Guidance

- Expected impact band: escrow/backing drift for rebasing tokens
- Expected severity band: medium

## False-Positive Cautions

- No issue if rebasing tokens are explicitly unsupported and blocked.
- No issue if conversion uses shares or regularly reconciles escrow balance changes.
- No issue if the token cannot change balances except through observed transfers.
