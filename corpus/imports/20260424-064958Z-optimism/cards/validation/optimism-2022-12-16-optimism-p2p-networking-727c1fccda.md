# Validation Card

## Metadata

- ID: `optimism-2022-12-16-optimism-p2p-networking-727c1fccda`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `uncaught-panic-on-untrusted-input`

## What Confirmed The Issue

- Adds guardGossipValidator that uses defer and recover() around pubsub.ValidatorEx.
- On panic, the wrapper logs the event and forces pubsub.ValidationReject, which is fail-closed behavior.
- The wrapper is applied in JoinGossip when registering the block gossip topic validator.
- The affected path processes peer-supplied gossip messages in the p2p subsystem, a security-sensitive input boundary.

## What Could Have Invalidated It

- No shown root cause for the underlying panic inside the validator.
- No proof that a remote peer could reliably trigger the panic with crafted input.
- No evidence of the pre-patch blast radius, such as whole-node crash versus isolated goroutine failure.
- No evidence of confidentiality, integrity, or consensus compromise beyond availability hardening.

## Severity Guidance

- Expected impact band: availability-or-liveness
- Expected severity band: medium_or_low

## False-Positive Cautions

- No shown root cause for the underlying panic inside the validator.
- No proof that a remote peer could reliably trigger the panic with crafted input.
- No evidence of the pre-patch blast radius, such as whole-node crash versus isolated goroutine failure.
