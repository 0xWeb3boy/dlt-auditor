# Root-Cause Card

## Metadata

- ID: `go-ethereum-2022-06-29-go-ethereum-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-terminal-block-validation-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch fixes a consensus validation gap in go-ethereum's beacon transition header verification. It adds explicit terminal total-difficulty validation for the PoW portion of mixed PoW/PoS header batches and preserves those validation failures during asynchronous result collection.
