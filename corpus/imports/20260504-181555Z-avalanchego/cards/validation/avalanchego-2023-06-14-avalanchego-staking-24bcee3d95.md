# Validation Card

## Metadata

- ID: `avalanchego-2023-06-14-avalanchego-staking-24bcee3d95`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence: verifyStopStakerAuthorization now rejects target transactions that do not implement txs.ContinuousStaker.
- Evidence: Permission verification now uses continuousStakerTx.ManagementKey() instead of owner fields derived from validator, delegator, or subnet transaction types.
- Evidence: The changed path governs StopStakerTx handling, a state-changing staking operation.

## What Could Have Invalidated It

- Compensating control: No explicit exploit scenario showing who could stop a staker before the patch.
- Compensating control: No test excerpt demonstrating an unauthorized reward owner or subnet owner was previously accepted.
- Compensating control: No commit body or advisory confirming a security vulnerability.

## Severity Guidance

- Expected impact band: medium_or_low_hardening
- Expected severity band: high_or_medium
- Severity rationale: Unauthorized validator lifecycle changes are high impact, but this record is likely hardening because exploitability is inferred from the authority change rather than proven end-to-end.

## False-Positive Cautions

- Caution: Supports authorization hardening for continuous staker stop operations.
- Caution: Does not support claims of asset theft, key compromise, or consensus takeover.
- Caution: Does not prove the old owner-selection behavior was exploitable on a live network.
