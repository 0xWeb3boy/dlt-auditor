# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-07-24-sei-chain-transaction-processing-9836e33a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vulnerable-cryptographic-dependency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cryptographic-dependency-freshness`

## Violated Invariant

- Invariant: Cryptographic parsing and signing call sites must use dependency versions and APIs that include known security fixes.

## Trust Boundary

- Boundary: untrusted public key or signature bytes -> cryptographic library verifier/parser

## Attack Surface

- Entrypoint type: crypto-parse-or-signature-verification-call
- Sensitive sink: accepting parsed public keys or verified signatures

## Impact Pattern

- Primary impact: unspecified-security-impact
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Upgrade vulnerable cryptographic dependencies and migrate affected public-key parsing call sites to the replacement API while preserving existing malformed-key handling. Public-key parsing is part of signer/address identity handling. The commit explicitly references dependency CVE fixes. Malformed public keys must continue to fail before address derivation or association proceeds.
