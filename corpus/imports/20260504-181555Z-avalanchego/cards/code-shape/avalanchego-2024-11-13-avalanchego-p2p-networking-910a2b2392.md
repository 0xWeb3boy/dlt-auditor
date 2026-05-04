# Code-Shape Card

## Metadata

- ID: `avalanchego-2024-11-13-avalanchego-p2p-networking-910a2b2392`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-protocol-message-verification`

## Code Shape Summary

- Warp message verification was wired into transaction and block acceptance paths. The reusable shape is an extension message whose validity depends on external network and validator context and must be checked everywhere the enclosing object is accepted.

## Search Motifs

- VerifyWarpMessages added in builder, manager, or block verifier
- message verification uses network ID, P-Chain height, and validator state
- block or tx paths fail closed on protocol message verification errors

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Call protocol-message verification at each transaction and block ingress point with the correct network, height, and validator-state context.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Feature implementation commits may add first-time verification rather than fix a reachable bypass
- Do not claim cross-chain forgery unless unchecked messages affected state
- Messages ignored by the VM are not sensitive sinks
