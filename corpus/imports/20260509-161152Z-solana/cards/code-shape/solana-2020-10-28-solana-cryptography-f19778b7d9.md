# Code-Shape Card

## Metadata

- ID: `solana-2020-10-28-solana-cryptography-f19778b7d9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-reflection-amplification`

## Code Shape Summary

Confirmed security fix for UDP gossip pull reflection/amplification. The patch adds ping-pong endpoint proof and gates gossip PullResponse generation on address validity plus prior ping response state, reducing the ability to spoof a PullRequest source address and induce larger responses to a victim.

## Search Motifs

- search for udp reflection amplification checks near cryptography entrypoints
- compare validation before and after the network-endpoint-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Require UDP endpoint proof before sending amplification-prone responses: verify ping/pong messages, cache successful ping responses, and gate large PullResponse generation on that reachability state.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
