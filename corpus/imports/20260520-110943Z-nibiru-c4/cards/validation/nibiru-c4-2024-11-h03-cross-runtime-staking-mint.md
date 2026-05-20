# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-h03-cross-runtime-staking-mint`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `cross-runtime-balance-desynchronization`

## What Confirmed The Issue

- Public C4 report section H-03 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue for denoms not mirrored into EVM StateDB.
- No issue if setBalance centrally synchronizes every balance-changing path.

## Severity Guidance

- Expected impact band: unbacked native token minting
- Expected severity band: high

## False-Positive Cautions

- No issue for denoms not mirrored into EVM StateDB.
- No issue if setBalance centrally synchronizes every balance-changing path.
- Need an EVM-visible stale balance to be committed after the native mutation.
