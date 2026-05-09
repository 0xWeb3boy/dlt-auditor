# Code-Shape Card

## Metadata

- ID: `solana-2020-10-28-solana-cryptography-ae91270961`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-amplification-via-source-spoofing`

## Code Shape Summary

Confirmed security fix for spoofed-source UDP amplification in Solana gossip pull handling. The commit body explicitly describes PullRequest source spoofing causing much larger PullResponse traffic to a victim, and the patch adds Ping/Pong handling plus a pull-request gate that filters requests before response generation unless the source address has passed the endpoint check.

## Search Motifs

- search for udp amplification via source spoofing checks near cryptography entrypoints
- compare validation before and after the network-endpoint-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add endpoint proof before amplification-prone UDP responses, cache successful ping-pong checks, verify Ping/Pong protocol messages, and gate PullRequest response generation on that proof.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
