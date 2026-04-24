# Root-Cause Card

## Metadata

- ID: `geth-arb-2015-05-15-go-ethereum-core-logic-5c1a7b965c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `peer-response-parent-binding`

## Violated Invariant

- Invariant: A peer response should only clear a pending validation challenge when it satisfies the exact expected relation, not merely when it contains a plausible hash.

## Trust Boundary

- Boundary: untrusted peer downloader response -> sync validation checkpoint

## Attack Surface

- Entrypoint type: peer hash or block response handler
- Sensitive sink: clearing pending cross-check state and continuing sync

## Impact Pattern

- Primary impact: sync-integrity
- Secondary impact: consensus-integrity
- Severity guide: high

## Short Reusable Lesson

- Downloader validation accepted a returned block hash without proving it matched the expected parent relationship for the pending cross-check. Bind pending validation state to the expected parent or context and clear it only when the response matches that exact tuple.
