# Validation Card

## Metadata

- ID: `sei-chain-2021-05-27-sei-chain-rpc-client-api-46c2d2fbd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ibc-client-recovery-hardening`

## What Confirmed The Issue

- Evidence 1: IBC client recovery affects light-client state used for future verification behavior.
- Evidence 2: Keeper now rejects substitute clients that are not ahead of the subject client.

## What Could Have Invalidated It

- Compensating control 1: The proposal fields are already constrained by governance validation and cannot affect copied state.
- Compensating control 2: The copied state is independently verified against the substitute client before storage.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The proposal fields are already constrained by governance validation and cannot affect copied state.
- Caution 2: The copied state is independently verified against the substitute client before storage.
