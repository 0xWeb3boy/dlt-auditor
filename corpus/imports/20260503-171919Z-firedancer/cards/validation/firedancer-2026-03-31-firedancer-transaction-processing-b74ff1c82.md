# Validation Card

## Metadata

- ID: `firedancer-2026-03-31-firedancer-transaction-processing-b74ff1c82`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-capacity-invariant-violation`

## What Confirmed The Issue

- Evidence 1: Runtime HTTP/2 receive path now checks total frame size against rx buffer capacity before waiting for complete frame data.
- Evidence 2: Oversized impossible-to-buffer frames now trigger FD_H2_ERR_INTERNAL instead of setting rx_suppress indefinitely.

## What Could Have Invalidated It

- Compensating control 1: No evidence that current production deployments were vulnerable; commit says production buffers are currently sized properly.
- Compensating control 2: No proof of remote exploitability unless a deployment can accept frames larger than its rx buffer capacity.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: No evidence that current production deployments were vulnerable; commit says production buffers are currently sized properly.
- Caution 2: No proof of remote exploitability unless a deployment can accept frames larger than its rx buffer capacity.
