# Root-Cause Card

## Metadata

- ID: `agave-2024-11-07-agave-consensus-f621667cd1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unauthenticated-constructor-exposure`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authenticated-construction`

## Violated Invariant

- Invariant: Production constructors for signed network metadata should require signing material or otherwise make unsigned construction impossible outside tests.

## Trust Boundary

- Boundary: `local-producer-api->p2p-gossip-state`

## Attack Surface

- Entrypoint type: `internal-constructor`
- Sensitive sink: CRDS gossip value creation and insertion
- Attacker capability: Influence or introduce production code paths that construct gossip metadata through exposed constructors.
- Key precondition: Unsigned construction is available outside test code.

## Impact Pattern

- Primary impact: `metadata-authenticity`
- Secondary impact: `p2p-integrity`
- Severity guidance: `low` because The patch removes an unsafe construction footgun in a signed gossip type, but the evidence did not show a production misuse or remote acceptance bypass.

## Short Reusable Lesson

- A signed gossip value type exposed both signed and unsigned constructors in production, leaving the authenticity invariant to caller discipline instead of the type interface.
- Structural fix: Make the signed constructor the public production path and restrict unsigned construction helpers to test-only/internal visibility.
