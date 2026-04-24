# Validation Card

## Metadata

- ID: `rippled-2025-06-02-rippled-transaction-processing-7e24adbdd`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: Commit body states the change fixes NFT transactions bypassing trustline authorization requirements.
- Evidence 2: Patch adds nft::checkTrustlineAuthorized checks before NFT offer acceptance proceeds on non-native issued assets.

## What Could Have Invalidated It

- Compensating control 1: No full implementation of nft::checkTrustlineAuthorized is shown.
- Compensating control 2: No regression test details are included in the supplied evidence.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: privilege-misuse
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No full implementation of nft::checkTrustlineAuthorized is shown.
- Caution 2: No regression test details are included in the supplied evidence.
