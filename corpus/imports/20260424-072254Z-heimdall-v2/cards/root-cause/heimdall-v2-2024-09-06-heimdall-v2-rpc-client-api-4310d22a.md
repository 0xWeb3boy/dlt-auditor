# Root-Cause Card

## Metadata

- ID: `heimdall-v2-2024-09-06-heimdall-v2-rpc-client-api-4310d22a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-extension-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: centralized validation of proposal-embedded vote extensions.

## Violated Invariant

- Invariant: proposal handlers must validate vote-extension signatures, validator context, and quorum before embedding or accepting vote-derived data.

## Trust Boundary

- Boundary: proposer and validator supplied vote-extension data crossing into proposal construction and proposal acceptance.

## Attack Surface

- Entrypoint type: ABCI PrepareProposal and ProcessProposal handlers.
- Sensitive sink: proposal acceptance decision and vote-derived transaction approvals.

## Impact Pattern

- Primary impact: validator attestation integrity.
- Secondary impact: consensus proposal integrity.

## Short Reusable Lesson

- Structural checks such as unmarshalling and duplicate detection are not substitutes for context-aware validator validation. Consensus handlers should call a shared routine that verifies signatures, quorum, height, proposer, round, and validator-set membership before accepting vote-derived data.
