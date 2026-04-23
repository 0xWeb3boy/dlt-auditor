# Root-Cause Card

## Metadata

- ID: `nitro-2023-10-13-nitro-storage-f88557d06`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-metering`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `complete-resource-accounting`

## Violated Invariant

- Invariant: Cross-language or offloaded execution should return consumed gas to the protocol layer so all activation work is charged exactly once before finalization.

## Trust Boundary

- Boundary: `ArbOS or Go caller->native or Rust activation engine`

## Attack Surface

- Entrypoint type: `gas-accounting-or-resource-charging`
- Sensitive sink: `burning or finalizing gas charges for activation work`

## Impact Pattern

- Primary impact: `resource-underpricing`
- Secondary impact: `none`

## Short Reusable Lesson

- Cross-language or offloaded execution should return consumed gas to the protocol layer so all activation work is charged exactly once before finalization. The evidence supports a likely security fix for undercharging in the native/JIT Stylus activation path. The patch adds explicit gas-in/gas-out handling across the ArbOS-to-Rust activation boundary and burns the consumed amount afterward. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
