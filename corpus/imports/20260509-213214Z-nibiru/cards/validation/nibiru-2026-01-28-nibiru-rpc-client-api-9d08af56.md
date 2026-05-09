# Validation Card

## Metadata

- ID: `nibiru-2026-01-28-nibiru-rpc-client-api-9d08af56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vulnerable-dependency`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: CometBFT consensus/networking library version used by the application.
- Evidence 2: The validated finding ties the change to this invariant: Consensus and networking dependencies with published security advisories must be upgraded to a patched version across every module that can build or test the node.

## What Could Have Invalidated It

- Compensating control 1: Dependency churn alone is not security without advisory or version evidence
- Compensating control 2: Do not invent the upstream root cause if the advisory details are absent

## Severity Guidance

- Expected impact band: `dependency_security`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-fix`.
- Caution 2: Security dependency fixes in consensus libraries are high-priority, but local exploit details were not present in the finding.
