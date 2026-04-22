# Root-Cause Card

## Metadata

- ID: `scroll-2025-09-29-scroll-transaction-processing-09ef1ddb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-input-selection`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-input-selection`

## Violated Invariant

- Invariant: Watcher logic should derive validium message state from the authoritative transaction set attached to the observed block rather than from reconstructed or stale auxiliary sources.

## Trust Boundary

- Boundary: `chain-data->watcher-state-derivation`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `derived cross-domain message state persisted or forwarded by the watcher`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Watcher logic should derive validium message state from the authoritative transaction set attached to the observed block rather than from reconstructed or stale auxiliary sources. The evidence supports a validium-specific correctness fix in how the watcher sources L1 message transactions before later processing. It does not, by itself, establish a vulnerability, exploit path, or concrete security impact, so the strongest justified classification is unclear rather than confirmed security. The robust fix is to thread the authoritative transaction set from the observed block through validium watcher processing instead of reconstructing message inputs from an alternate source.
