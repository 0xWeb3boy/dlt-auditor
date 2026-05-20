# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-small-type-alu-overflow-33331`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `narrow-integer-overflow-check-missing`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `declared-width-overflow-enforcement`

## Violated Invariant

- Operations on u8, u16, and u32 must enforce those widths even when the VM evaluates them in u64 registers.

## Trust Boundary

- Boundary: `contract-input->standard-library-math`
- Entrypoint type: `library-function`
- Sensitive sink: `narrow integer value that may be displayed or ABI-encoded differently than stored`

## Attack Surface

- Choose pow operands that overflow a narrow type but not u64.
- Rely on downstream code or SDK wrapping behavior.

## Exploit Preconditions

- Narrow integer values are compiled into u64 storage.
- pow lacks manual narrow-width overflow checks.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- When a compiler widens small types internally, every library operation must preserve the source-level type contract.
