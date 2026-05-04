# Code-Shape Card

## Metadata

- ID: `snarkos-2022-11-29-snarkos-p2p-networking-607d5a7ec`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `p2p-handshake-authentication-hardening`

## Code Shape Summary

- Handshake challenge responses lack explicit nonce/signature authentication material or verification inputs needed to bind peer address to the live session.

## Search Motifs

- challenge response contains genesis header but no signature
- verify_challenge_response lacks peer address or expected nonce
- handshake signs counterparty nonce only after patch

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Add nonce signing to challenge responses and verify response data against peer identity, expected genesis header, and expected nonce.

## False Match Warnings

- If peer identity is not trusted for any later decision, impact is reduced
- Transport-level mutual authentication can compensate
- Do not infer full exploit without evidence that unauthenticated sessions become privileged
