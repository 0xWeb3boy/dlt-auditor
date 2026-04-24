# Code-Shape Card

## Metadata

- ID: `rippled-2025-06-02-rippled-transaction-processing-7e24adbdd`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The patch fixes an authorization enforcement gap in NFTokenAcceptOffer::preclaim for non-native issued-asset NFT offer acceptance. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact authorization check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Add explicit, feature-gated trustline authorization checks in preclaim for non-native issued-asset NFT offer acceptance paths before continuing transaction processing.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Add explicit, feature-gated trustline authorization checks in preclaim for non-native issued-asset NFT offer acceptance paths before continuing transaction processing.

## False Match Warnings

- No full implementation of nft::checkTrustlineAuthorized is shown.
- No regression test details are included in the supplied evidence.
