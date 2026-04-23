# Root-Cause Card

## Metadata

- ID: `go-ethereum-2017-02-13-go-ethereum-storage-e23e86921`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `content-integrity verification`

## Violated Invariant

- Invariant: Data accepted under a content-derived identifier must hash to that identifier before the system stores or trusts it.

## Trust Boundary

- Boundary: Peer-supplied chunk payloads -> local content-addressed storage and repair paths.

## Attack Surface

- Entrypoint type: Peer store request.
- Sensitive sink: Persisting or serving chunk bytes under a trusted content key.

## Impact Pattern

- Primary impact: Content and storage integrity degradation.
- Secondary impact: Corrupt local records that require repair or cleanup.

## Short Reusable Lesson

- In content-addressed systems, the advertised key is only a claim. The implementation must recompute the digest from the received bytes at every trust boundary where those bytes can enter or re-enter durable state.
