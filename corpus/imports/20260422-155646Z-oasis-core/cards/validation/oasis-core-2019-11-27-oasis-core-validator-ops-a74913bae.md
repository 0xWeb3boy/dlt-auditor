# Validation Card

## Metadata

- ID: `oasis-core-2019-11-27-oasis-core-validator-ops-a74913bae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-debug-configuration`

## What Confirmed The Issue

- Evidence 1: The patch inserts an early sanity check in 'loadOrGenerateEntity' that blocks 'AllowEntitySignedNodes' unless the unsafe debug flag is set. The remaining provided hunks rename constants used by registry CLI code.
- Evidence 2: The source finding states the invariant explicitly: The registry CLI should not proceed with entity-signed-node mode unless the operator has explicitly enabled the corresponding unsafe debug acknowledgement.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `low`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
