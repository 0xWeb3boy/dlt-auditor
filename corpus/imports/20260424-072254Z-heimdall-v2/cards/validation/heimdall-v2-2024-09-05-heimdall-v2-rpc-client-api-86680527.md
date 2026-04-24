# Validation Card

## Metadata

- ID: `heimdall-v2-2024-09-05-heimdall-v2-rpc-client-api-86680527`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-height-validation`

## What Confirmed The Issue

- Evidence 1: `PreBlocker` now passes the authoritative request height into vote tallying.
- Evidence 2: aggregation now rejects decoded vote extensions when embedded height does not equal `currentHeight-1`.

## What Could Have Invalidated It

- Compensating control 1: the consensus engine or signature scheme already rejects mismatched-height vote extensions before application aggregation.
- Compensating control 2: embedded height is unused metadata and cannot influence tallying or state transitions.

## Severity Guidance

- Expected impact band: consensus-integrity / replay-resistance hardening.
- Expected severity band: medium.

## False-Positive Cautions

- Caution 1: do not infer RPC exposure from a vote-extension aggregation patch.
- Caution 2: do not claim chain halt or exploitability without evidence that mismatched-height payloads could be accepted in production.
