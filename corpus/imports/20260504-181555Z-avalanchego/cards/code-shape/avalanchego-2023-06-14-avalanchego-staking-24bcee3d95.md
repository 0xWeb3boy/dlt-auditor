# Code-Shape Card

## Metadata

- ID: `avalanchego-2023-06-14-avalanchego-staking-24bcee3d95`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- Stop-staker authorization was changed to require the target continuous staker management key. The reusable shape is a lifecycle operation that previously authorized against adjacent owner fields instead of the object-specific management authority.

## Search Motifs

- StopStaker authorization using reward owner or subnet owner
- type checks for ContinuousStaker before permission verification
- ManagementKey introduced as the authorization source

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Type-check the referenced staker, extract its explicit management key, and verify the submitted credentials against that key before applying lifecycle changes.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- If reward owner and management key are always identical by construction, the issue may collapse to refactoring
- Do not flag read-only staker lookups as authorization sinks
- Unsupported transaction type rejection is only security-relevant when it gates a state-changing action
