# Validation Card

## Metadata

- ID: `go-ethereum-2018-09-20-go-ethereum-storage-d6254f827`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-choice-tie-break-hardening`

## What Confirmed The Issue

- Evidence 1: core/blockchain.go changes canonical-chain reorg selection for equal total difficulty blocks.
- Evidence 2: Old behavior randomly reorged on same-height equal-TD competitors with 50% probability.

## What Could Have Invalidated It

- Compensating control 1: Classify as fork-choice hardening, not a confirmed security fix.
- Compensating control 2: Do not claim remote exploitability from the supplied patch alone.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Classify as fork-choice hardening, not a confirmed security fix.
- Caution 2: Do not claim remote exploitability from the supplied patch alone.
