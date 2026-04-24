# Validation Card

## Metadata

- ID: `reth-2023-01-13-reth-p2p-networking-5c80bc912`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-validation`

## What Confirmed The Issue

- Before the patch, DiscoveryEvent::Discovered directly called add_peer(peer_id, socket_addr, fork_id) without a visible fork-ID validity check.
- After the patch, discovery no longer inserts peers directly and instead routes them through StateAction::DiscoveredNode.

## What Could Have Invalidated It

- No evidence shows that an invalid-fork peer could successfully handshake, stay connected, or influence consensus-critical behavior
- No test, incident, or exploit evidence demonstrates real-world impact beyond admitting incompatible peers

## Severity Guidance

- Expected impact band: network_policy_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No evidence shows that an invalid-fork peer could successfully handshake, stay connected, or influence consensus-critical behavior
- No test, incident, or exploit evidence demonstrates real-world impact beyond admitting incompatible peers
