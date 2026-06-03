# Validation Card

Record: `omni-cantina-h06-same-block-staking-event-order-loss`
Project: `omni-network`
Source finding: `Omni Cantina H-6`

## Positive Confirmation

Confirm evmEvents sorts by address/topics/data, Delegate topic sorts first, and deliverDelegate fails before deliverCreateValidator for same-block workflows.

## Preconditions To Confirm

- EVMEvent sorting ignores source log index.
- Delegate event topic sorts before CreateValidator.
- deliverDelegate fails if validator does not exist.
- Failed event delivery is skipped.

## False-Positive Cautions

- The source contract forbids same-block create/delegate or refunds value.
- Original log index is included in the sorted key.
- Failed delegate delivery blocks head advancement or retries.

## Minimal Reproduction Or Check

Create source logs in order CreateValidator then Delegate and assert native delivery applies Delegate first unless log index is preserved.
