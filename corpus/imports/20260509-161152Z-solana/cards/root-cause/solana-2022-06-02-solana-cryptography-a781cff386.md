# Root-Cause Card

## Metadata

- ID: `solana-2022-06-02-solana-cryptography-a781cff386`
- Bug family: `staking_registry_and_accountability`
- Bug class: `quic-stake-admission-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The grounded root cause is incomplete or mismatched forwarding-path behavior: QUIC connection handling was not visibly guarded by stake or unstaked-connection budget in the supplied snippet, and banking-stage forwarding used a caller-supplied forwarding address rather than deriving the destination from the active ForwardOption. The evidence does not support a cryptographic, replay, or consensus-safety root cause.

## Impact Pattern

- Primary impact: unauthorized-connection-admission, resource-exhaustion-risk
- Expected band: integrity_or_funds
- Severity guide: Medium

## Short Reusable Lesson

The provided evidence supports a Solana TPU/QUIC transaction-forwarding functional fix with possible resource-control hardening, not a confirmed vulnerability fix. The patch gates QUIC connection handling on nonzero stake or available unstaked-connection capacity, changes banking-stage forwarding to derive destinations from ForwardOption, handles NotForward earlier, and corrects a TPU shutdown log message. Claims about cryptography, replay protection, f...
