# Root-Cause Card

## Metadata

- ID: `fuel-core-2025-04-08-fuel-core-cryptography-8b3d741d2c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-binding-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separation`

## Violated Invariant

- Delegation signatures must bind replay-sensitive metadata, including nonce, inside the signed entity rather than carrying it as mutable side-channel data.

## Trust Boundary

- Boundary: `delegate-message->preconfirmation-authority`
- Entrypoint type: `p2p-message-handler`
- Sensitive sink: `delegate key acceptance and preconfirmation signing authority`

## Attack Surface

- Relay or replay delegate messages with altered or reused nonce metadata.
- Observe signed delegation objects on the p2p path.

## Exploit Preconditions

- Nonce or equivalent freshness data is transported outside the signed delegation object.
- Receivers rely on that nonce to distinguish delegate key instances.

## Impact Pattern

- Primary impact: `request-forgery-or-replay`
- Secondary impact: `signature-confusion`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Replay-protection metadata must live inside the cryptographic envelope whose freshness it is meant to protect.
