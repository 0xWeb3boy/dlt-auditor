# Root-Cause Card

## Metadata

- ID: `solana-2020-03-16-solana-cryptography-dc347dd3d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-state-consistency-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-root-consistency`

## Violated Invariant

- Protocol input must satisfy state root consistency before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The grounded gap was lack of a surfaced, opt-in halt mechanism for detecting accounts-state hash divergence against configured trusted validators. The evidence does not support claims about invalid signature handling, replay acceptance, remote exploitability, fund loss, or arbitrary state corruption.

## Impact Pattern

- Primary impact: consensus-integrity, validator-state-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The evidence supports an opt-in Solana validator accounts-hash consistency check that can halt a node on mismatch with configured trusted validators. It does not establish a concrete vulnerability, attacker path, default exposure, or prior exploitable consensus failure. Treat this as potentially security-relevant hardening, not a validated vulnerability fix.
