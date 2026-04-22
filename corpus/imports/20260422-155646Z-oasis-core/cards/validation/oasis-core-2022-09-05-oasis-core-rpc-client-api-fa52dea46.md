# Validation Card

## Metadata

- ID: `oasis-core-2022-09-05-oasis-core-rpc-client-api-fa52dea46`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `freshness-verification`

## What Confirmed The Issue

- Evidence 1: The patch introduces a 'ProveFreshness' host handler that submits a dedicated registry transaction and receives a proof of inclusion. Supporting APIs were added so the proof can be produced by the backend and returned over gRPC instead of collapsing the operation to success-or-error only. The supplied excerpts do not show the consuming verifier logic.
- Evidence 2: The source finding states the invariant explicitly: If client or TEE freshness is enforced, the decision should rely on recent consensus-anchored evidence rather than a bare transaction-submission success result. The provided excerpts only show plumbing toward that invariant, not the full enforcement point.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
