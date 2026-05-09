# Root-Cause Card

## Metadata

- ID: `solana-2021-02-13-solana-transaction-processing-99012f022e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-size-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The Hash base58 parser lacked a pre-decode encoded-length bound. It still checked decoded byte length afterward, so the demonstrated issue is unbounded decoder input at the parser boundary, not an established acceptance of invalid hashes.

## Impact Pattern

- Primary impact: parser-hardening, resource-exhaustion-mitigation
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch adds a maximum base58 string length check to Solana SDK Hash parsing. Hash::from_str now rejects strings longer than 44 characters with ParseHashError::WrongSize before calling bs58::decode. This is grounded as input-size validation and parser hardening, but the evidence does not prove a vulnerability or show that oversized input causes a security impact.
