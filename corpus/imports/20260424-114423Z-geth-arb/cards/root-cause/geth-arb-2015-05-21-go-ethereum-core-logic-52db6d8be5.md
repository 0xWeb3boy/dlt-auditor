# Root-Cause Card

## Metadata

- ID: `geth-arb-2015-05-21-go-ethereum-core-logic-52db6d8be5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `queued-parent-cross-check-binding`

## Violated Invariant

- Invariant: Cross-checks must validate the exact expected predecessor or parent relation before downloaded data is trusted for chain assembly.

## Trust Boundary

- Boundary: untrusted peer sync response -> downloader validation queue

## Attack Surface

- Entrypoint type: peer block or hash response handler
- Sensitive sink: validated sync progress and chain assembly

## Impact Pattern

- Primary impact: sync-integrity
- Secondary impact: consensus-integrity
- Severity guide: high

## Short Reusable Lesson

- The downloader treated a parent hash as valid when it was merely present in local queue state rather than equal to the expected parent for that challenge. Record the expected parent for each pending check and compare responses against that recorded value before accepting them.
