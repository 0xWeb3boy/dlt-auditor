# Code-Shape Card

## Metadata

- ID: `solana-2021-01-21-solana-transaction-processing-9dd5d4407b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-bound-validation`

## Code Shape Summary

The patch adds pre-decode maximum encoded-length checks to Solana SDK `Signature::from_str` and `Pubkey::from_str`. This is grounded input hardening for base58 parsing, but the provided evidence does not establish a concrete vulnerability, attacker entry point, denial-of-service impact, signature bypass, key substitution, replay issue, or consensus effect.

## Search Motifs

- search for input bound validation checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit maximum encoded-length validation at the parser boundary before invoking base58 decoding for fixed-size values, while retaining post-decode exact-size validation.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
