# Validation Card

## Metadata

- ID: `rippled-2022-05-30-rippled-core-logic-0ecfc7cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`

## What Confirmed The Issue

- Evidence 1: Commit body explicitly says SHA-256 replaced SHA-1 for generated certificates.
- Evidence 2: Commit body says CBC-based ciphers were removed from the default cipher list to avoid potential security issues including cited CVEs.

## What Could Have Invalidated It

- Compensating control 1: Supplied patch excerpts do not show the actual defaultCipherList before/after contents.
- Compensating control 2: Supplied patch excerpts do not show the certificate-generation changes directly.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: correctness-or-hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: Supplied patch excerpts do not show the actual defaultCipherList before/after contents.
- Caution 2: Supplied patch excerpts do not show the certificate-generation changes directly.
