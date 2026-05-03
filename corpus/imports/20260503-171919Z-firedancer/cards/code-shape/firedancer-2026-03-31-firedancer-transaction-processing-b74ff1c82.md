# Code-Shape Card

## Metadata

- ID: `firedancer-2026-03-31-firedancer-transaction-processing-b74ff1c82`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-capacity-invariant-violation`

## Code Shape Summary

- The receive state machine assumed the configured buffer was always large enough for any accepted non-DATA frame, so an impossible header-plus-payload size relationship could stall progress indefinitely.

## Search Motifs

- Motif 1: non-DATA frame size compared against receive buffer capacity
- Motif 2: state machine waits forever on a header plus payload that can never fit
- Motif 3: frame parser adds an impossible-capacity fail-fast check

## Typical Asymmetry

- The peer controls frame size, but the receiver trusts a local buffer-capacity invariant that may not actually hold.

## Patch Pattern

- Validate declared frame size against configured receive capacity up front and fail closed instead of waiting on impossible progress.

## False Match Warnings

- No evidence that current production deployments were vulnerable; commit says production buffers are currently sized properly.
- No proof of remote exploitability unless a deployment can accept frames larger than its rx buffer capacity.
