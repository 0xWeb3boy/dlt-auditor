# Validation Card

Record: `omni-cantina-h05-consensus-key-squatting-no-pop`
Project: `omni-network`
Source finding: `Omni Cantina H-5`

## Positive Confirmation

Trace createValidator to native MsgCreateValidator and confirm no consensus-key signature is required before duplicate-key rejection.

## Preconditions To Confirm

- Staking.sol does not bind whitelisted operator to pubkey.
- createValidator does not require proof-of-possession.
- Native staking rejects duplicate consensus pubkeys after EVM funds are accepted.

## False-Positive Cautions

- Operational off-chain checks are not enough unless enforced on-chain.
- The attacker cannot reach createValidator under current allowlist and no future permissionless path exists.
- The victim can recover or retry funds automatically.

## Minimal Reproduction Or Check

Process two createValidator events with the same pubkey and different operators; assert the second fails downstream and the source-side funds need recovery.
