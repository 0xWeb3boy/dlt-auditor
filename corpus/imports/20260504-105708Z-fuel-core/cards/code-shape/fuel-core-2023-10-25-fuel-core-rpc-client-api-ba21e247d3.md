# Code-Shape Card

## Metadata

- ID: `fuel-core-2023-10-25-fuel-core-rpc-client-api-ba21e247d3`
- Bug family: `resource_accounting_and_limits`
- Bug class: `p2p-reserved-peer-reputation-hardening`

## Code Shape Summary

- P2P validation returned a single reject outcome that was consumed by gossip scoring without preserving whether the source was reserved or whether the invalidity was race-dependent.

## Search Motifs

- MessageAcceptance::Reject used for reserved peer traffic
- reserved propagation source punished by gossip score
- invalid transaction after block race
- reject converted to ignore for trusted peer

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Normalize reserved-source validation failures that are policy-neutral into Ignore before reputation handling, and broaden internal service plumbing to carry the distinction.

## False Match Warnings

- Rejecting malformed or adversarial payloads from untrusted peers is expected.
- Reputation changes are lower risk if they cannot affect peer eviction, banning, or routing.
