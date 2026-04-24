# Validation Card

## Metadata

- ID: `sei-chain-2026-04-10-sei-chain-core-logic-107c8e793`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation-hardening`

## What Confirmed The Issue

- Evidence 1: P2P mux header handling now receives the full header and validates the stream kind field directly.
- Evidence 2: New inbound stream creation rejects missing h.Kind instead of allowing GetKind to default to stream kind 0.

## What Could Have Invalidated It

- Compensating control 1: The transport authenticates and fixes stream kind before mux handling.
- Compensating control 2: Kind is informational and not used for limits or routing.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The transport authenticates and fixes stream kind before mux handling.
- Caution 2: Kind is informational and not used for limits or routing.
