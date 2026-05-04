# Validation Card

## Metadata

- ID: `moonbeam-2020-05-13-moonbeam-cryptography-fb437475f4`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`

## What Confirmed The Issue

- State-mutating session persistence calls changed from signed origin/raw vectors to ensure_none with structured signed payloads.
- Old shown code wrote selected validators and snapshots from caller-provided values into persistent storage.

## What Could Have Invalidated It

- A complete validate_unsigned implementation proving equivalent pre-dispatch authorization before the old writes
- Evidence that the old signed calls were never exposed or were root/admin gated elsewhere

## Severity Guidance

- Expected impact band: authorization_to_session_state
- Expected severity band: medium

## False-Positive Cautions

- Unsigned extrinsics are safe when validate_unsigned checks payload signature, freshness, and replay keys
- Signed administrative-only calls may be acceptable if governance/root is the only origin
