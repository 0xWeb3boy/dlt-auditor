# Code-Shape Card

## Metadata

- ID: `snarkos-2024-01-17-snarkos-p2p-networking-34b5c3586`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`

## Code Shape Summary

- Challenge responses sign only the requester-provided nonce, leaving response-side freshness outside the authenticated transcript.

## Search Motifs

- signature over challenge nonce only
- response contains nonce not included in signed bytes
- verify builds signed bytes missing response-side freshness

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Add a response nonce, include it in the response schema, sign the combined challenge and response nonce bytes, and verify the exact transcript.

## False Match Warnings

- If an outer channel binds the full transcript, the bug may be mitigated
- Nonce-schema migrations without verifier changes are not enough
- Do not conflate with private-key exposure
