# Code-Shape Card

## Metadata

- ID: `zksync-2020-12-10-zksync-transaction-processing-e81d133a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insecure-default-secret-detection`

## Code Shape Summary

- Configuration loading now detects sample admin/prover auth secrets outside localhost and emits explicit errors. The reusable shape is deployment config accepting known default credentials for privileged services without environment-sensitive safety checks.

## Search Motifs

- ADMIN_SERVER_SECRET_AUTH or PROVER_SECRET_AUTH compared with sample
- ETH_NETWORK != localhost guard around secret warning
- startup config validation for default/shared auth secret

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Add environment-aware startup validation that detects known sample secrets for privileged auth configuration and raises explicit operator-visible errors.

## False Match Warnings

- A log-only warning is weaker than refusal to start.
- Sample secrets in tests, localhost, or dev fixtures are expected.
- Panic message improvements in auth code are not the core security fix.
