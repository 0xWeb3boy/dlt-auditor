# Root-Cause Card

## Metadata

- ID: `moonbeam-2021-12-15-moonbeam-transaction-processing-aa99e9353b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-domain-separation-and-origin-authentication`

## Violated Invariant

- Invariant: A signed authorization must be scoped to the intended network/domain and bound to an authenticated origin before it can change reward address state.

## Trust Boundary

- Boundary: Externally supplied signed reward authorization crosses into runtime reward-account mapping.

## Attack Surface

- Entrypoint type: signed-reward-address-association
- Sensitive sink: crowdloan reward address association/change

## Impact Pattern

- Primary impact: request-forgery-or-replay
- Secondary impact: unauthorized-action, reward-redirection

## Short Reusable Lesson

- Runtime config exposed reward address operations without visible per-network signature domain constants. The patch added signed origins and network-specific SignatureNetworkIdentifier values. Wire authenticated origins and per-network signature domain identifiers into reward authorization runtime configuration.
