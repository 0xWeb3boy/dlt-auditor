# Root-Cause Card

## Metadata

- ID: `sei-chain-2021-05-27-sei-chain-rpc-client-api-46c2d2fbd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ibc-client-recovery-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `recovery-state-selection`

## Violated Invariant

- Invariant: Recovery or substitution flows must derive copied consensus state from verified live client state, not from proposal-supplied historical ranges.

## Trust Boundary

- Boundary: governance or recovery proposal -> light-client consensus state store

## Attack Surface

- Entrypoint type: governance-recovery-handler
- Sensitive sink: updating client recovery metadata and consensus states

## Impact Pattern

- Primary impact: consensus-client-integrity
- Secondary impact: state-consistency

## Short Reusable Lesson

- Remove caller-supplied recovery range selection, enforce substitute-client preconditions at the proposal entry point, and copy the substitute client's latest consensus state directly. IBC client recovery affects future verification behavior for the recovered client. Using a single latest substitute consensus state is clearer than copying a sparse range selected through proposal input.
