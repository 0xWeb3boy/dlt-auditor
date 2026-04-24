# Code-Shape Card

## Metadata

- ID: `geth-arb-2018-02-12-go-ethereum-p2p-networking-9123eceb0f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reply-correlation-hardening`

## Code Shape Summary

- The pong path accepted replies by node identity without checking that the reply token matched the outstanding ping packet.

## Search Motifs

- reply accepted for peer ID without request token match
- pong or ack lacks nonce/hash correlation
- request completion keyed too broadly by node identity
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that request-reply-correlation was enforced only partially, late, or in one branch while another path could still reach node bonding, liveness confirmation, or request completion.

## Patch Pattern

- Store the encoded request token and compare the reply token before marking the request complete.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
