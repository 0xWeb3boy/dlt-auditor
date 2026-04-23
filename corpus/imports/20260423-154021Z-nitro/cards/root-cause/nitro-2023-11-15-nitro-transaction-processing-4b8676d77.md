# Root-Cause Card

## Metadata

- ID: `nitro-2023-11-15-nitro-transaction-processing-4b8676d77`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-index-derivation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authoritative-index-derivation`

## Violated Invariant

- Invariant: Proof generation and machine-hash lookups should derive message indices from authoritative batch metadata and reject ambiguous equal-boundary ranges.

## Trust Boundary

- Boundary: `batch metadata->proof generation and state-provider lookups`

## Attack Surface

- Entrypoint type: `proof-generation-or-state-provider-query`
- Sensitive sink: `generating a proof or machine hash at a selected message index`

## Impact Pattern

- Primary impact: `state-consistency`
- Secondary impact: `proof-generation-integrity`

## Short Reusable Lesson

- Proof generation and machine-hash lookups should derive message indices from authoritative batch metadata and reject ambiguous equal-boundary ranges. The supplied diff supports a correctness fix in the staker state-provider path: proof and machine-hash lookups now derive the message index from batch metadata, equal-batch ranges are rejected, and missing batch-count data is surfaced as a catch-up condition. The evidence does not establish an exploitable vulnerability, invalid proof acceptance, or consensus impact. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
