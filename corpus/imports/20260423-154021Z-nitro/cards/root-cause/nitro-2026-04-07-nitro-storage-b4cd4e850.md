# Root-Cause Card

## Metadata

- ID: `nitro-2026-04-07-nitro-storage-b4cd4e850`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-guard`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `bounded-recovery-resource-growth`

## Violated Invariant

- Invariant: Recovery handlers should bound stack-growth retries and only perform expensive recovery once in the allowed execution context.

## Trust Boundary

- Boundary: `runtime trap->native stack-overflow recovery path`

## Attack Surface

- Entrypoint type: `runtime-recovery-path`
- Sensitive sink: `repeating stack growth or fault recovery until resources are exhausted`

## Impact Pattern

- Primary impact: `availability`
- Secondary impact: `none`

## Short Reusable Lesson

- Recovery handlers should bound stack-growth retries and only perform expensive recovery once in the allowed execution context. The patch is best supported as runtime hardening for native stack-overflow handling, not as a demonstrated security fix. The shown changes bound stack-growth retry behavior and update tests around that path, but the provided evidence does not establish an exploitable vulnerability or a protocol-level security violation. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
