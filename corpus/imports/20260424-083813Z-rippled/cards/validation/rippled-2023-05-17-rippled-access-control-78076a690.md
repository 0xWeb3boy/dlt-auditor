# Validation Card

## Metadata

- ID: `rippled-2023-05-17-rippled-access-control-78076a690`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-acceptance`

## What Confirmed The Issue

- Evidence 1: Commit message says accepting secrets or passphrases in account fields is considered a bug and a potential security hole.
- Evidence 2: Patch changes multiple RPC account handlers to parse only AccountID values with parseBase58<AccountID>.

## What Could Have Invalidated It

- Compensating control 1: No evidence shows secrets were actually written to logs, errors, or responses.
- Compensating control 2: No evidence shows an authorization bypass or access to protected account data.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: credential-exposure-risk
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence shows secrets were actually written to logs, errors, or responses.
- Caution 2: No evidence shows an authorization bypass or access to protected account data.
