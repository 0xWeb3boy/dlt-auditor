# Root-Cause Card

## Metadata

- ID: `go-ethereum-2020-12-08-go-ethereum-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`
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

- The evidence supports replay-protection hardening in go-ethereum contract binding transaction option creation. The patch adds chainID-aware signer construction and routes mobile keyed transaction options and relevant tests through `NewKeyedTransactorWithChainID`. It does not establish an access-control flaw, privilege bypass, or proven exploit.
