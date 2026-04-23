# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-05-21-go-ethereum-core-logic-52db6d8be`
- Bug family: `authz_and_role_gates`
- Bug class: `cross-check-validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization`

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

- The patch fixes a downloader validation weakness where forged blocks could satisfy cross-checks by pointing their parent hash at any known queued hash. The fix records the expected parent hash with each pending cross-check and requires the returned block to match it exactly.
