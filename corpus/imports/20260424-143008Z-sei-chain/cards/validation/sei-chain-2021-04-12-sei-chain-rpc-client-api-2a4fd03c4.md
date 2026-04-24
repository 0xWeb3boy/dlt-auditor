# Validation Card

## Metadata

- ID: `sei-chain-2021-04-12-sei-chain-rpc-client-api-2a4fd03c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `failed-ack-state-rollback`

## What Confirmed The Issue

- Evidence 1: RecvPacket now executes OnRecvPacket inside ctx.CacheContext() instead of the live context.
- Evidence 2: Cached callback writes are committed only when ack is nil/asynchronous or ack.Success() is true.

## What Could Have Invalidated It

- Compensating control 1: The callback is read-only or all writes occur after acknowledgement success is checked.
- Compensating control 2: A lower layer already wraps the whole receive path in a transactional context and discards failed acknowledgements.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The callback is read-only or all writes occur after acknowledgement success is checked.
- Caution 2: A lower layer already wraps the whole receive path in a transactional context and discards failed acknowledgements.
