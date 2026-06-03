# Code-Shape Card

Record: `omni-cantina-h05-consensus-key-squatting-no-pop`
Project: `omni-network`
Source finding: `Omni Cantina H-5`

## Search Shape

The source staking contract accepts any 33-byte consensus key from an allowed operator, while the native uniqueness check happens after source-side value acceptance.

## Motifs

- `createValidator pubkey`
- `isAllowedValidator`
- `no proof of possession`
- `MsgCreateValidator`
- `another validator with this pubkey`
- `duplicate consensus key`
- `funds locked in Staking.sol`

## Negative Signals

- On-chain allowlist binds each operator to an exact pubkey.
- createValidator requires a signature from the consensus key.
- Failed duplicate-key delivery automatically refunds source funds.

## Likely Fix Shape

Require proof-of-possession over operator, chain, and registration intent; reserve pubkeys at the source boundary or refund failed native delivery.
