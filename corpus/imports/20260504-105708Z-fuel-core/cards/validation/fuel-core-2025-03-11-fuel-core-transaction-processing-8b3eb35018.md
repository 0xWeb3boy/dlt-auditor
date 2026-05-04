# Validation Card

## Metadata

- ID: `fuel-core-2025-03-11-fuel-core-transaction-processing-8b3eb35018`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`
- Security verdict: `confirmed`
- Validated as: `security-fix`

## What Confirmed The Issue

- Patch calls check_preconfirmation_signature(&sealed) before status processing.
- Regression tests exercise fake signature verification success and failure.

## What Could Have Invalidated It

- All upstream callers already verify the exact sealed message and reject failures.
- The status manager treats unauthenticated statuses as non-authoritative hints.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Confirmed missing signature verification allows forged or unauthorized status changes in a security-sensitive preconfirmation path. Impact is high for clients depending on those statuses.

## False-Positive Cautions

- No issue if the message source is authenticated by a stronger channel and payload signatures are redundant by design.
- No issue if statuses are never exposed or trusted by clients.
