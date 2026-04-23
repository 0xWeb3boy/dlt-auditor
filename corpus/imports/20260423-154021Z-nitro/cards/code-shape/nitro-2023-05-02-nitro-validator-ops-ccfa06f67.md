# Code-Shape Card

## Metadata

- ID: `nitro-2023-05-02-nitro-validator-ops-ccfa06f67`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-validator-configuration`

## Code Shape Summary

- Short description of what the buggy code looked like: The strongest supported change is a validator/staker startup hardening in `cmd/nitro/nitro.go`: active staker strategies now auto-enable `BlockValidator` unless the dangerous override is set. That supports a configuration-safety reading, but the provided evidence does not establish a concrete vulnerability, attacker path, or demonstrated security impact.

## Search Motifs

- Motif 1: safer validator flags are optional until patches invert them to defaults
- Motif 2: dangerous overrides are introduced to preserve legacy behavior while tightening defaults
- Motif 3: staker mode implicitly requires validation checks that the config surface did not enforce

## Typical Asymmetry

- What was checked in one path but missing in another: The code exposed a policy-sensitive parameter or mode choice at a higher layer, even though the underlying action was supposed to be bound to a narrower trusted destination or safer default.

## Patch Pattern

- What the fix changed structurally: Convert a safer validator setting from manual configuration into a defaulted startup rule, while preserving an explicitly named dangerous override for opting out.

## False Match Warnings

- What looks similar but is often not a bug: If the destination or mode is deterministically overwritten later, similar parameter flow may be harmless.
