# Validation Card

## Metadata

- ID: `zksync-2020-12-10-zksync-transaction-processing-e81d133a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insecure-default-secret-detection`

## What Confirmed The Issue

- Config loading checks admin and prover auth secrets against the sample value.
- The check is gated to non-localhost networks.
- The patch does not establish transaction-processing or malformed-input impact.

## What Could Have Invalidated It

- The sample value is impossible in production config or replaced before use.
- The warning is unreachable or not visible to operators.

## Severity Guidance

- Expected impact band: `configuration_auth_hardening`
- Expected severity band: `medium_or_low`
- Rationale: Default-secret detection is valuable hardening, but the patch logs errors rather than proving exploitability or enforcing startup failure.

## False-Positive Cautions

- A log-only warning is weaker than refusal to start.
- Sample secrets in tests, localhost, or dev fixtures are expected.
