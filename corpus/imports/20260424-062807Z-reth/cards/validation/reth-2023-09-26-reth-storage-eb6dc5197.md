# Validation Card

## Metadata

- ID: `reth-2023-09-26-reth-storage-eb6dc5197`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-validation`

## What Confirmed The Issue

- ensure_well_formed_payload now documents and enforces that pre-Cancun blocks must not contain blob transactions.
- The new check gates behavior on is_cancun_active_at_timestamp(block.timestamp) and block.has_blob_transactions(), showing fork-rule enforcement.

## What Could Have Invalidated It

- No pre-patch execution trace proves such payloads were previously accepted through to canonical processing
- No test or runtime evidence shows a consensus split, chain halt, or remotely triggerable exploit

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No pre-patch execution trace proves such payloads were previously accepted through to canonical processing
- No test or runtime evidence shows a consensus split, chain halt, or remotely triggerable exploit
