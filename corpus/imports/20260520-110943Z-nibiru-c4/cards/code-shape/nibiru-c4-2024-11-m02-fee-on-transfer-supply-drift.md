# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m02-fee-on-transfer-supply-drift`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fee-on-transfer-supply-drift`

## Code Shape Summary

- convertCoinToEvmBornERC20 transferred the full requested ERC20 amount but burned only actualSentAmount after transfer fees.

## Search Motifs

- actualSentAmount from ERC20 Transfer
- burnCoin uses actualSentAmount
- fee-on-transfer token conversion
- bank coin supply invariant comment

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Burn the full bank coin input amount on conversion back to ERC20 and document that outbound token fees reduce the recipient ERC20 amount.

## False Match Warnings

- No issue if fee-on-transfer tokens are excluded.
- No issue if the full input bank coin is burned regardless of ERC20 transfer fee.
- No issue if conversion accounting explicitly mints/burns fee-adjusted shares rather than fixed-denom bank coins.
