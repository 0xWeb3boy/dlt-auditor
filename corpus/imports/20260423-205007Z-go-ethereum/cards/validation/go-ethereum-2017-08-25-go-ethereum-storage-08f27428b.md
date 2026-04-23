# Validation Card

## Metadata

- ID: `go-ethereum-2017-08-25-go-ethereum-storage-08f27428b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `contract-address-collision`

## What Confirmed The Issue

- Evidence 1: EVM.Create now computes the destination address before account creation and checks StateDB.GetNonce for occupancy.
- Evidence 2: EVM.Create now checks StateDB.GetCodeHash and rejects addresses with existing non-empty code.

## What Could Have Invalidated It

- Compensating control 1: Treat as protocol security hardening, not a proven vulnerability fix.
- Compensating control 2: Do not claim demonstrated state corruption or storage overwrite from the supplied evidence alone.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Treat as protocol security hardening, not a proven vulnerability fix.
- Caution 2: Do not claim demonstrated state corruption or storage overwrite from the supplied evidence alone.
