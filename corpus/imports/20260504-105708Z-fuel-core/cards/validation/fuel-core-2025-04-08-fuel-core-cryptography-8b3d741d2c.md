# Validation Card

## Metadata

- ID: `fuel-core-2025-04-08-fuel-core-cryptography-8b3d741d2c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-binding-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch changes Delegate to wrap SignedByBlockProducerDelegation.
- Preconfirmation signature service now creates delegate keys with nonce in the signed entity.

## What Could Have Invalidated It

- A prior domain-separated signature already covered the nonce through another field.
- Delegate messages are never accepted from untrusted or replayable channels.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Binding nonce into the signed object prevents replay or metadata substitution classes. Evidence supports hardening, not a demonstrated exploit.

## False-Positive Cautions

- No issue if the external nonce is independently MACed or checked against an authenticated transcript.
- No issue if nonce is informational and not used for replay protection.
