# Validation Card

## Metadata

- ID: `movement-2025-04-24-movement-cryptography-d16aa9e0d`
- Bug family: `authz_and_role_gates`
- Bug class: `transaction-validation-bypass`

## What Confirmed The Issue

- whitelisted_accounts None previously produced prevalidator None.
- batch_write previously branched on self.prevalidator and could avoid calling prevalidate.
- The patched code always calls self.prevalidator.prevalidate(transaction) and pushes only Ok(Prevalidated(transaction)).

## What Could Have Invalidated It

- No-whitelist deployments are never exposed to untrusted submitters.
- A separate mandatory validator runs before batch_write in all configurations.
- Validator::new performs no baseline checks, making the change only structural.

## Severity Guidance

- Expected impact band: integrity_medium
- Expected severity band: medium_or_low
- Rationale: A validation bypass at sequencer ingestion is security-relevant, but Phase 4 did not prove an end-to-end exploit or consensus break.

## False-Positive Cautions

- Do not flag if no-whitelist mode is unreachable or explicitly trusted/admin-only.
- Do not claim whitelist enforcement was broken when a whitelist was configured.
