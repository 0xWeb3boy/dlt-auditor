# Root-Cause Card

## Metadata

- ID: `solana-2018-07-08-solana-cryptography-71f05cb23e`
- Bug family: `authz_and_role_gates`
- Bug class: `timestamp-source-authorization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach consensus, accounting, or authorization-sensitive state.

## Trust Boundary

- Boundary: untrusted external input to protocol enforcement layer

## Attack Surface

- Entrypoint type: protocol input or state-transition entrypoint
- Sensitive sink: consensus, accounting, or authorization-sensitive state

## Root Cause

The budget condition evaluation did not receive the public key associated with the witness source, so timestamp satisfaction could be based on the timestamp witness value alone rather than on whether the timestamp came from a contract-approved authority.

## Impact Pattern

- Primary impact: unauthorized-condition-satisfaction
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch fixes budget timestamp witness evaluation so future-payment conditions are checked against an explicit source public key before a locked budget can reduce to a payment. The evidence supports a contract-level authorization fix for timestamp sources, without proving a full exploit path or concrete loss.
