# Root-Cause Card

## Metadata

- ID: `solana-2021-01-21-solana-transaction-processing-9dd5d4407b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-bound-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The parser boundary lacked an encoded-string length bound before base58 decoding, so overlong inputs that could not be valid fixed-size signatures or public keys still reached decode logic.

## Impact Pattern

- Primary impact: resource-exhaustion-hardening
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch adds pre-decode maximum encoded-length checks to Solana SDK `Signature::from_str` and `Pubkey::from_str`. This is grounded input hardening for base58 parsing, but the provided evidence does not establish a concrete vulnerability, attacker entry point, denial-of-service impact, signature bypass, key substitution, replay issue, or consensus effect.
