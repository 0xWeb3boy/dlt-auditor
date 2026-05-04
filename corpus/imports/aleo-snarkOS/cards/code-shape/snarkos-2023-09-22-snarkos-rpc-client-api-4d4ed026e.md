# Code-Shape Card

## Metadata

- ID: `snarkos-2023-09-22-snarkos-rpc-client-api-4d4ed026e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-request-response-correlation`

## Code Shape Summary

- Validator discovery response handling enforces response size but lacks a peer-specific outstanding-request check before using the validator list.

## Search Motifs

- response handler checks list size but not outstanding request
- contains_outbound_*_request added before processing response
- decrement request counter after accepting peer response

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Track outbound validator requests per peer, reject responses without a matching request, and decrement the counter when accepted.

## False Match Warnings

- Broadcast announcements intentionally processed without request are different
- If response data is ignored unless separately verified, severity drops
- A global request flag is weaker than peer-specific correlation
