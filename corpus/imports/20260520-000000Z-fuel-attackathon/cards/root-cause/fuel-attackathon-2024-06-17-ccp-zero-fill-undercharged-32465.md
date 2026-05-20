# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ccp-zero-fill-undercharged-32465`
- Bug family: `resource_accounting_and_limits`
- Bug class: `undercharged-memory-zero-fill`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Gas charged for a memory-copy opcode must cover all bytes written or zero-filled by the opcode.

## Trust Boundary

- Boundary: `transaction-bytecode->vm-memory`
- Entrypoint type: `vm-opcode`
- Sensitive sink: `large memory zero-fill performed at low gas cost`

## Attack Surface

- Execute CCP with an offset beyond contract code and a large requested copy length.
- Use the zero-fill behavior as a cheap memory clear.

## Exploit Preconditions

- CCP charges based on contract bytecode size rather than the requested output length.
- Out-of-range source data causes destination bytes to be zero-filled.

## Impact Pattern

- Primary impact: `fee-bypass`
- Secondary impact: `resource-exhaustion`
- Blast radius: `chain-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Meter the actual resource effect of an opcode, including implicit writes such as padding and zero fill.
