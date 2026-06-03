# Validation Card

Record: `omni-cantina-m04-empty-transaction-proposal-bloat`
Project: `omni-network`
Source finding: `Omni Cantina M-4`

## Positive Confirmation

Confirm a proposal with many empty transactions runs TxDecoder for each and is accepted because no unexpected messages appear.

## Preconditions To Confirm

- ProcessProposal iterates all req.Txs.
- Only message type counts are bounded.
- Transactions with no messages are accepted and skipped.
- The intended honest proposal contains a single transaction.

## False-Positive Cautions

- The consensus layer already enforces a small transaction count.
- Empty transactions fail decoding or are rejected by ante processing on this path.
- The application genuinely supports multiple independent generated transactions.

## Minimal Reproduction Or Check

Construct a proposal with many empty-message txs and assert the fixed router rejects count greater than one or empty-message txs.
