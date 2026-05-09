# Code-Shape Card

## Metadata

- ID: `solana-2020-10-29-solana-cryptography-06067dd823`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-amplification-missing-endpoint-validation`

## Code Shape Summary

The patch addresses a UDP gossip amplification issue in Solana pull-request handling. The commit explicitly cites a HackerOne report describing spoofed PullRequest source addresses causing larger PullResponse packets to be sent to victims, and the code evidence shows a new ping-pong endpoint check before pull responses are generated.

## Search Motifs

- search for udp amplification missing endpoint validation checks near cryptography entrypoints
- compare validation before and after the network-endpoint-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Require endpoint reachability proof before sending larger UDP responses. Challenge the claimed source address with ping-pong verification, cache successful endpoints, and gate amplification-prone response generation on that verification.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
