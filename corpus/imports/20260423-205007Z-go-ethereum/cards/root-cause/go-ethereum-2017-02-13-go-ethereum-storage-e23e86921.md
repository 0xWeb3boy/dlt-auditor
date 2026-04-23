# Root-Cause Card

## Metadata

- ID: `go-ethereum-2017-02-13-go-ethereum-storage-e23e86921`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Swarm chunks are content-addressed: incoming or persisted chunk bytes must hash to the advertised chunk key before being accepted or treated as valid.

## Trust Boundary

- Boundary: Peer-supplied synchronization or protocol data crossing into local validation and scheduling logic.

## Attack Surface

- Entrypoint type: `p2p message`
- Sensitive sink: `consensus-visible state transition or journal replay`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The grounded security-relevant change is that Swarm store-request handling now hashes incoming chunk data and rejects it when it does not match the advertised key.
