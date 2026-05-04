# Code-Shape Card

## Metadata

- ID: `snarkos-2022-03-08-snarkos-rpc-client-api-894cb0136`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-message-framing-hardening`

## Code Shape Summary

- Crawler networking code classifies framed messages early but may not drain unwanted payloads before continuing to parse the stream.

## Search Motifs

- read message type then continue without consuming body
- unbounded expected-message buffer
- deserialize full frame before checking whether type is wanted

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Read minimal frame metadata first, enforce bounded expected-message sizes, skip unnecessary deserialization, and drain discarded payloads.

## False Match Warnings

- Crawler-only code has lower chain-security impact
- If each frame is on a fresh connection, stream alignment is irrelevant
- A lower codec layer may already drain rejected frames
