# Validation Card

## Metadata

- ID: `oasis-core-2023-04-12-oasis-core-cryptography-97f265501`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-secret-validation`

## What Confirmed The Issue

- Evidence 1: The patch swaps one-shot secret fetches for provider-backed iteration so non-matching replicated candidates can be skipped, constrains startup ephemeral-secret import to a recent bounded range, and makes proposal persistence explicitly runtime/generation-scoped in the shown tests. These changes harden integrity and robustness of the rotation flow, but the supplied evidence does not prove a full attack scenario.
- Evidence 2: The source finding states the invariant explicitly: Replicated or persisted master-secret state should only affect rotation when it is bound to the correct runtime and generation and matches the expected checksum chain; replicated values are untrusted until verified.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
