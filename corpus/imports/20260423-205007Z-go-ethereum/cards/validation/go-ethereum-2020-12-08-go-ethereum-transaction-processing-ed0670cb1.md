# Validation Card

## Metadata

- ID: `go-ethereum-2020-12-08-go-ethereum-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`

## What Confirmed The Issue

- Evidence 1: Commit message states previous contract interactions used the Homestead signer and now users can specify Homestead or EIP-155 plus chainID.
- Evidence 2: `mobile/bind.go` changes keyed transact option creation to accept `chainID` and call `NewKeyedTransactorWithChainID`.

## What Could Have Invalidated It

- Compensating control 1: Classify as replay-protection hardening, not access control.
- Compensating control 2: Do not claim a proven security fix for an exploited vulnerability.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Classify as replay-protection hardening, not access control.
- Caution 2: Do not claim a proven security fix for an exploited vulnerability.
