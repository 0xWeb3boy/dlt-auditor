# Code-Shape Card

## Metadata

- ID: `rippled-2018-10-23-rippled-cryptography-c1a02440d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-list-redirect-scheme-hardening`

## Code Shape Summary

- The draft correctly rejects the unsupported replay/signature-validation theory. The grounded change is that validator-site redirects now reject schemes other than http and https while the commit adds explicit configured file:// validator-list support. Reusable shape: check for trust-root-and-freshness-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: signature-verification-path missing exact trust-root-and-freshness-validation check before accepted signature, signer identity, manifest, or replay-sensitive object
- Motif 2: security-sensitive path reaches accepted signature, signer identity, manifest, or replay-sensitive object before rejecting malformed, stale, or unauthorized input
- Motif 3: Add an explicit URL-scheme allowlist on redirect handling and use explicit error-code-based file reads for configuration inputs.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into accepted signature, signer identity, manifest, or replay-sensitive object unless the trust-root-and-freshness-validation gate runs before the state-changing branch.

## Patch Pattern

- Add an explicit URL-scheme allowlist on redirect handling and use explicit error-code-based file reads for configuration inputs.

## False Match Warnings

- No proof that an attacker could control a validator-list redirect in a meaningful threat model.
- No proof of local file disclosure, validator-list validation bypass, replay, signature bypass, or consensus compromise.
