# Root-Cause Card

## Metadata

- ID: `nitro-2023-05-02-nitro-validator-ops-ccfa06f67`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-validator-configuration`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `safe-validator-defaults`

## Violated Invariant

- Invariant: Validator or staker modes should default to the safer validation setting unless the operator explicitly opts out with a clearly dangerous override.

## Trust Boundary

- Boundary: `operator configuration->validator or staker startup policy`

## Attack Surface

- Entrypoint type: `node-startup-or-configuration`
- Sensitive sink: `starting validator duties with weakened safety checks`

## Impact Pattern

- Primary impact: `integrity-hardening`
- Secondary impact: `none`

## Short Reusable Lesson

- Validator or staker modes should default to the safer validation setting unless the operator explicitly opts out with a clearly dangerous override. The strongest supported change is a validator/staker startup hardening in `cmd/nitro/nitro.go`: active staker strategies now auto-enable `BlockValidator` unless the dangerous override is set. That supports a configuration-safety reading, but the provided evidence does not establish a concrete vulnerability, attacker path, or demonstrated security impact. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
