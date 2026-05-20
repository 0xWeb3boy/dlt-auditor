# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-cross-contract-stack-overflow-33519`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `stack-frame-overwrite-across-calls`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stack-frame-bound-enforcement`

## Violated Invariant

- Cross-contract call frames must not silently overwrite adjacent locals, arguments, or return data.

## Trust Boundary

- Boundary: `callee-call-frame->caller-memory`
- Entrypoint type: `cross-contract-call`
- Sensitive sink: `stack memory holding local variables and call arguments`

## Attack Surface

- Deploy or invoke contracts with large variables around cross-contract calls.
- Influence call paths that allocate wide values such as u256.

## Exploit Preconditions

- Compiler or runtime frame sizing lets values exceed the allocated stack region.
- No trap is raised before adjacent memory is overwritten.

## Impact Pattern

- Primary impact: `memory-integrity`
- Secondary impact: `state-integrity`
- Blast radius: `contract-local`
- Severity guess: `critical`

## Short Reusable Lesson

- Compiler-generated call-frame layouts need explicit memory bounds whenever user code can compose large values and nested calls.
