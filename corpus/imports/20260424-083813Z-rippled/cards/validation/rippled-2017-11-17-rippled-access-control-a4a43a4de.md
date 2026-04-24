# Validation Card

## Metadata

- ID: `rippled-2017-11-17-rippled-access-control-a4a43a4de`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `tls-sni-hostname-setup`

## What Confirmed The Issue

- Evidence 1: HTTPClient.cpp now calls mSocket.setTLSHostName(mDeqSites[0]) before connecting when sslVerify() is true.
- Evidence 2: The added comment explicitly ties the change to verified SSL connections and server name indication before connection.

## What Could Have Invalidated It

- Compensating control 1: No evidence that certificate verification was previously disabled or bypassed.
- Compensating control 2: No evidence that a wrong certificate was previously accepted.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: tls-certificate-validation-hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence that certificate verification was previously disabled or bypassed.
- Caution 2: No evidence that a wrong certificate was previously accepted.
