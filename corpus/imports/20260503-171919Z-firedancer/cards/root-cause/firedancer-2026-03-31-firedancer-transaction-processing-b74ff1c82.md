# Root-Cause Card

## Metadata

- ID: `firedancer-2026-03-31-firedancer-transaction-processing-b74ff1c82`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-capacity-invariant-violation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `buffer-capacity-versus-frame-size-validation`

## Violated Invariant

- Invariant: A framed receive state machine must reject headers whose declared frame size can never fit within the configured receive buffer.

## Trust Boundary

- Boundary: Peer-controlled HTTP/2 frame headers crossing into the local receive buffer state machine.

## Attack Surface

- Entrypoint type: framed network receive state machine
- Sensitive sink: frame assembly progress and receive buffer capacity accounting

## Impact Pattern

- Primary impact: availability
- Secondary impact: resource-capacity hardening

## Short Reusable Lesson

- The receive state machine assumed the configured buffer was always large enough for any accepted non-DATA frame, so an impossible header-plus-payload size relationship could stall progress indefinitely.
