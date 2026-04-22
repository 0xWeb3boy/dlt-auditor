# Validation Card

## Metadata

- ID: `oasis-core-2023-02-01-oasis-core-rpc-client-api-8eabf0d47`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-validation`

## What Confirmed The Issue

- Evidence 1: The fix changes 'generateStatus' so committee admission no longer trusts the first matching runtime registration. Instead, it carries the relevant status fields into a loop over all of the node's runtime entries, counts supported versions, and only admits the node when every supported key manager runtime version matches the expected status.
- Evidence 2: The source finding states the invariant explicitly: Key manager committee membership should be derived only from nodes whose supported key manager runtime versions all conform to the authoritative key manager status. Accepting a node based on only the first matching runtime entry is insufficient.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
