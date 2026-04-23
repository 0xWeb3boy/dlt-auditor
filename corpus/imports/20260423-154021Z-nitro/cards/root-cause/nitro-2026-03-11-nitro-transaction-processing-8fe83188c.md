# Root-Cause Card

## Metadata

- ID: `nitro-2026-03-11-nitro-transaction-processing-8fe83188c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-integrity-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `mandatory-accumulator-continuity-check`

## Violated Invariant

- Invariant: Delayed-message sequencing should always perform accumulator continuity and reorg checks before appending messages, regardless of execution mode.

## Trust Boundary

- Boundary: `delayed-message backlog->sequencing path`

## Attack Surface

- Entrypoint type: `sequencing-or-delayed-message-processing`
- Sensitive sink: `sequencing delayed messages into chain state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Delayed-message sequencing should always perform accumulator continuity and reorg checks before appending messages, regardless of execution mode. The patch appears to remove a MEL-specific gap where delayed-message sequencing could skip an accumulator continuity/reorg check and adds MEL support code needed to perform that check. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
