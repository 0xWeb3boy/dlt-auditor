# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-05-04-stellar-core-storage-37668bf24`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-state-invariant`

## Code Shape Summary

- Authorization flag and allow-trust handlers changed issuer policy state without proving that existing trustlines and revocation authority allowed the transition.

## Search Motifs

- AUTH_REQUIRED_FLAG set after issued balances
- AUTH_REVOCABLE_FLAG changed after trustlines exist
- allowTrust revocation without revocable flag
- hasIssued predicate added for issuer state

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Add precondition checks before authorization-state transitions and introduce a ledger predicate that detects existing positive-balance trustlines.

## False Match Warnings

- Administrative flag changes before any credit issuance may be valid.
- Revocation is expected when the issuer explicitly enabled revocable authorization.
- Non-asset account flags may not have trustline-state coupling.
