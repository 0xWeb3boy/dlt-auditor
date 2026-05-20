# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m08-rebasing-token-escrow-drift`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `rebasing-token-escrow-supply-drift`

## Code Shape Summary

- Conversion logic assumed escrowed ERC20 balance remains aligned with minted bank coin supply between conversion events, which rebasing tokens violate without transfer callbacks.

## Search Motifs

- balance changes outside transfers
- rebasing ERC20 in FunToken mapping
- escrow balance may be lower than bank coin supply
- convertCoinToEvmBornERC20 assumes module ERC20 fund

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Reject rebasing/balance-mutating tokens from conversion or introduce an accounting model that reconciles escrow balance changes before redemption.

## False Match Warnings

- No issue if rebasing tokens are explicitly unsupported and blocked.
- No issue if conversion uses shares or regularly reconciles escrow balance changes.
- No issue if the token cannot change balances except through observed transfers.
