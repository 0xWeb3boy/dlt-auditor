# Code-Shape Card

## Metadata

- ID: `snarkos-2023-06-15-snarkos-rpc-client-api-5cc2764ae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-deserialization`

## Code Shape Summary

- Message-specific bincode deserializers call default deserialize_from without configured decode limits for peer-controlled messages containing collections.

## Search Motifs

- bincode::deserialize_from(&mut bytes.reader()) in peer message
- deserialize collection field without with_limit
- codec has max size constant not reused by message parser

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Use bincode options with MAXIMUM_MESSAGE_SIZE, fixed integer encoding, and trailing-byte policy at each affected deserialize site.

## False Match Warnings

- A lower layer that already bounds the exact byte slice reduces but may not remove allocation risk
- Small fixed-size message structs are less concerning
- Non-peer test fixtures are not attack surface
