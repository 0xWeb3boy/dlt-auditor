# Root-Cause Card

## Metadata

- ID: `geth-arb-2015-05-14-go-ethereum-transaction-processing-a4246c2da6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unknown-parent-sync-stall`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `parent-availability-progress-check`

## Violated Invariant

- Invariant: Sync progress must distinguish temporary absence from an invalid or unknown parent so a bad peer cannot stall queue advancement through ambiguous empty results.

## Trust Boundary

- Boundary: peer-supplied block sequence -> downloader queue and chain assembly

## Attack Surface

- Entrypoint type: peer sync response handler
- Sensitive sink: download scheduling and canonical chain extension

## Impact Pattern

- Primary impact: sync-availability
- Secondary impact: denial-of-service
- Severity guide: low-medium

## Short Reusable Lesson

- The downloader returned the same result for no-ready-work and unknown-parent cases, making a parent gap harder to treat as invalid peer input. Return an explicit unknown-parent signal and handle it as a peer or queue validation failure instead of ordinary no-work state.
