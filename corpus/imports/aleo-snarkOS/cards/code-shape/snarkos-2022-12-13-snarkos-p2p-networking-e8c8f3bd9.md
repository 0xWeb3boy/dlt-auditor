# Code-Shape Card

## Metadata

- ID: `snarkos-2022-12-13-snarkos-p2p-networking-e8c8f3bd9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-peer-address-resolution`

## Code Shape Summary

- Protocol error handling passes the observed SocketAddr directly to disconnect logic even though the router tracks the peer under a different listener address.

## Search Motifs

- disconnect(peer_addr) after process_message error
- listener_addr lookup added before disconnect
- connection SocketAddr used as peer identity key

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Resolve the connection address to the router-tracked listener address before invoking disconnect enforcement.

## False Match Warnings

- If connection and listener addresses are always identical, issue is correctness only
- Errors from trusted local peers reduce attack relevance
- No security issue if disconnect is advisory
