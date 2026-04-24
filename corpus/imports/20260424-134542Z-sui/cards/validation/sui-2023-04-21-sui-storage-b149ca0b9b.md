# Validation Card

## Metadata

- ID: `sui-2023-04-21-sui-storage-b149ca0b9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `wallet-content-script-message-validation`

## What Confirmed The Issue

- Commit body states that sites with no permissions cannot access wallet data after the change.
- Commit body states that wallet-popup messages sent from sites are ignored.
- ContentScriptConnection adds an explicit error path for unknown message payloads.
- Changed tests include site-to-content-script messaging coverage, indicating regression coverage around the wallet interface boundary.

## What Could Have Invalidated It

- No full before/after code for the permission decision is supplied.
- No test assertion excerpts show the exact no-permission wallet-data behavior.
- The visible implementation hunk only shows unknown-message rejection, not the wallet data access path itself.
- No advisory, issue details, or exploit scenario are provided.

## Severity Guidance

- Expected impact band: unauthorized-wallet-data-access-prevention_or_message-boundary-hardening
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Do not classify this as a storage or consensus issue based on the supplied evidence.
- Do not claim proven wallet data theft or a concrete exploitable vulnerability.
- The Playwright webServer/local validator changes are test infrastructure, not security evidence by themselves.
- The supported claim is conservative hardening of wallet extension site/content-script message handling.
