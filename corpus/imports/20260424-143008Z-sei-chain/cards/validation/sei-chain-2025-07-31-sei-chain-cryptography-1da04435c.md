# Validation Card

## Metadata

- ID: `sei-chain-2025-07-31-sei-chain-cryptography-1da04435c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Evidence 1: NewPartSetFromHeader now guards header.Total against MaxBlockPartsCount and avoids constructing normal arrays from excessive values.
- Evidence 2: defaultSetProposal now rejects proposals whose BlockID.PartSetHeader.Total exceeds MaxBlockPartsCount with ErrInvalidProposalPartSetHeader.

## What Could Have Invalidated It

- Compensating control 1: The field is already bounded by decoding or network framing before allocation.
- Compensating control 2: The value is locally derived from a verified block.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The field is already bounded by decoding or network framing before allocation.
- Caution 2: The value is locally derived from a verified block.
