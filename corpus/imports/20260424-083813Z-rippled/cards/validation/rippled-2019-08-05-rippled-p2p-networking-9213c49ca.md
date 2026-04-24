# Validation Card

## Metadata

- ID: `rippled-2019-08-05-rippled-p2p-networking-9213c49ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `tls-client-config-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject says ValidatorSites now honor SSL config settings.
- Evidence 2: SSLHTTPDownloader now calls ssl_ctx_.preConnectVerify before async_connect and fails on error.

## What Could Have Invalidated It

- Compensating control 1: No issue text for #2990 is provided.
- Compensating control 2: No exploit scenario or attacker-controlled network path is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: outbound-tls-verification-hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No issue text for #2990 is provided.
- Caution 2: No exploit scenario or attacker-controlled network path is shown.
