# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-impl-dependency-name-collision-32973`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `compiler-symbol-identity-collision`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `unique-symbol-identity`

## Violated Invariant

- Distinct impl blocks must have stable unique identities so their dependencies cannot overwrite each other.

## Trust Boundary

- Boundary: `source-declaration->compiler-dependency-map`
- Entrypoint type: `compiler-semantic-analysis`
- Sensitive sink: `dependency chain and type resolution used for code generation`

## Attack Surface

- Declare multiple impl blocks with colliding synthesized names.
- Use modules with same-named types so overwritten dependencies resolve to the wrong symbol.

## Exploit Preconditions

- Impl block identity is derived from concatenated declaration names.
- Dependencies are stored in one map keyed by that non-unique identity.

## Impact Pattern

- Primary impact: `incorrect-codegen`
- Secondary impact: `type-confusion`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Compiler symbol maps should key by stable unique identities, never by lossy display names or concatenated child names.
