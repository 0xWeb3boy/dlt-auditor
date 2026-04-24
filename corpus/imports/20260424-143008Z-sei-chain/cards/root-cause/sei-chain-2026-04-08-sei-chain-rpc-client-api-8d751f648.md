# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-04-08-sei-chain-rpc-client-api-8d751f648`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-protobuf-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `required-consensus-field-validation`

## Violated Invariant

- Invariant: Decoded consensus objects must reject missing or empty required fields before becoming domain objects.

## Trust Boundary

- Boundary: protobuf/wire decoded consensus message -> internal consensus type

## Attack Surface

- Entrypoint type: protobuf-to-domain-converter
- Sensitive sink: constructing TimeoutQC or proposal domain objects

## Impact Pattern

- Primary impact: malformed-input-rejection
- Secondary impact: consensus-hardening

## Short Reusable Lesson

- Add explicit validation at decode boundaries for required consensus fields and reject empty vote sets before constructing or accepting domain objects. Add malformed-protobuf tests to ensure decoders return errors instead of panicking. Prevents empty TimeoutQC protobufs from decoding successfully. Improves handling of malformed protobuf messages with missing fields.
