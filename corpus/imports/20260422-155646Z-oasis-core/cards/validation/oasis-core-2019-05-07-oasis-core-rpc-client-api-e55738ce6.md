# Validation Card

## Metadata

- ID: `oasis-core-2019-05-07-oasis-core-rpc-client-api-e55738ce6`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `key-scope-isolation`

## What Confirmed The Issue

- Evidence 1: From the supplied evidence, the concrete code-level fix is limited to two visible changes: exposing 'RAK' through the common 'Signer' trait and replacing the shown generic storage path in the keymanager host handler with runtime-scoped local storage access. The broader hardening claims in the commit description should be treated as stated intent rather than fully validated from the snippets alone.
- Evidence 2: The source finding states the invariant explicitly: Key-management responses and stored key material should be scoped to the intended runtime or contract and authenticated through the runtime attestation key when exposed over shared runtime paths. The provided snippets suggest movement toward that model, but they do not establish the full protocol or a concrete violated invariant before the patch.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `scope_or_confidentiality_boundary`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
