# Validation Card

## Metadata

- ID: `zksync-era-2023-12-06-zksync-era-core-logic-8a8cad6ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `dependency-vulnerability-remediation`

## What Confirmed The Issue

- Evidence 1: The commit and cargo-deny context identify rsa v0.6.1 / RUSTSEC-2023-0071 in the transitive dependency chain.
- Evidence 2: The manifest upgrades google-cloud-storage and google-cloud-auth to versions intended to remove that vulnerable transitive dependency.

## What Could Have Invalidated It

- Compensating control 1: The vulnerable crate is absent from the resolved production dependency graph or is dev/test-only.
- Compensating control 2: No reachable path exercises the vulnerable cryptographic primitive with secret material or observable timings.

## Severity Guidance

- Expected impact band: dependency-hardening
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Do not claim private-key recovery without application-specific timing-oracle evidence.
- Caution 2: Lockfile churn without an advisory or production dependency path is not enough.
