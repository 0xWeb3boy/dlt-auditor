# Root-Cause Card

## Metadata

- ID: `nitro-2022-05-31-nitro-transaction-processing-6d8c634ba`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-initialization-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `initialization-identity-check`

## Violated Invariant

- Invariant: Chain initialization should bind startup configuration to the intended genesis identity and reject mismatches before processing messages or state.

## Trust Boundary

- Boundary: `init message and chain config->startup initialization`

## Attack Surface

- Entrypoint type: `node-startup-or-initialization`
- Sensitive sink: `starting chain processing with a selected configuration`

## Impact Pattern

- Primary impact: `configuration-integrity`
- Secondary impact: `consensus-integrity`

## Short Reusable Lesson

- Chain initialization should bind startup configuration to the intended genesis identity and reject mismatches before processing messages or state. The provided evidence shows a configuration-binding fix: the code now carries `genesisBlockNum` through chain-config selection and checks it against the init message during startup. That supports a correctness or consensus-hardening interpretation, but the supplied material does not establish a concrete vulnerability or attacker-driven exploit path. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
