# Validation Card

## Metadata

- ID: `oasis-core-2019-11-13-oasis-core-rpc-client-api-75e2e189e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-malformed-input`

## What Confirmed The Issue

- Evidence 1: The patch makes 'PublicKey.UnmarshalBinary' fail unless the input length is exactly 'PublicKeySize'. It changes 'ToMapKey' to stop panicking on malformed keys, changes 'MarshalBinary' to serialize malformed keys as an all-zero key documented as blacklisted/invalid, and updates 'VerifyRegisterEntityArgs' to reject malformed node IDs before duplicate detection uses them.
- Evidence 2: The source finding states the invariant explicitly: Public keys used as identities must decode to exactly 'PublicKeySize' bytes, and malformed keys must be rejected or handled as invalid values without panicking during later map-key conversion or registry validation.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
