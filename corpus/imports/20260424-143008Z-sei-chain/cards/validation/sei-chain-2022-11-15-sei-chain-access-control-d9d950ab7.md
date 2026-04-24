# Validation Card

## Metadata

- ID: `sei-chain-2022-11-15-sei-chain-access-control-d9d950ab7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: RegisterContract now fetches wasm contract metadata with WasmKeeper.GetContractInfo for msg.Contract.ContractAddr.
- Evidence 2: The new code rejects registration when contractInfo.Creator != msg.Creator using sdkerrors.ErrUnauthorized.

## What Could Have Invalidated It

- Compensating control 1: A prior ante or router layer already proves the sender is the contract creator.
- Compensating control 2: The registration has no privileged effect or is purely informational.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: A prior ante or router layer already proves the sender is the contract creator.
- Caution 2: The registration has no privileged effect or is purely informational.
