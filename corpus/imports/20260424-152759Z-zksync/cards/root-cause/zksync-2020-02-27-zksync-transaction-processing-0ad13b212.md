# Root-Cause Card

## Metadata

- ID: `zksync-2020-02-27-zksync-transaction-processing-0ad13b212`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-message-domain-separation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `human-readable-authorization-domain`

## Violated Invariant

- Invariant: A wallet signature authorizing account-control changes should clearly bind the protocol, action, account, and new key so users and verifiers are not relying on opaque bytes.

## Trust Boundary

- Boundary: External wallet/user signing flow crosses into account-control authorization for ChangePubKey.

## Attack Surface

- Entrypoint type: `wallet_signature_authorization`
- Sensitive sink: ChangePubKey Ethereum authorization accepted by transaction processing

## Impact Pattern

- Primary impact: authorization clarity and domain-separation hardening
- Secondary impact: reduced blind-signing or replay ambiguity

## Short Reusable Lesson

- The patch changes ChangePubKey Ethereum authorization from opaque raw bytes to a protocol-specific registration message. The reusable pattern is account-control signatures whose prompts or signed payloads lack clear action/domain semantics.
