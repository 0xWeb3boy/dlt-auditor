# Validation Card

## Metadata

- ID: `sei-chain-2024-04-15-sei-chain-rpc-client-api-78eb1d663`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-address-association-check`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says unassociated EOA addresses are disallowed from using precompiles.
- Evidence 2: Changed handlers replace GetEVMAddressFromBech32OrDefault or GetEVMAddressOrDefault with GetEVMAddress plus found checks.

## What Could Have Invalidated It

- Compensating control 1: The generated payload is never used for privileged execution.
- Compensating control 2: Every downstream precompile revalidates the address association.

## Severity Guidance

- Expected impact band: authorization-or-identity-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The generated payload is never used for privileged execution.
- Caution 2: Every downstream precompile revalidates the address association.
