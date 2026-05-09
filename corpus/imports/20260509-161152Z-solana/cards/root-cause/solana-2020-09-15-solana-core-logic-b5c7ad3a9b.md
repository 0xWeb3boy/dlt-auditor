# Root-Cause Card

## Metadata

- ID: `solana-2020-09-15-solana-core-logic-b5c7ad3a9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-network-exposure-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `freshness-and-origin-validation`

## Violated Invariant

- Protocol input must satisfy freshness and origin validation before it can reach network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout.

## Trust Boundary

- Boundary: untrusted peer network traffic to validator networking pipeline

## Attack Surface

- Entrypoint type: peer packet, gossip value, repair response, or QUIC/UDP ingress
- Sensitive sink: network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout

## Root Cause

The pre-change code lacked the newly added opt-in controls for a more restricted validator networking posture. The evidence does not show that this absence was exploitable or that it broke consensus, ledger integrity, cryptographic authentication, or replay protection.

## Impact Pattern

- Primary impact: attack-surface-reduction, network-exposure-reduction
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds validator startup options for more restrictive deployments, including a restricted repair-only mode and a gossip validator allowlist. The evidence supports network exposure reduction and configuration hardening, but not a confirmed vulnerability fix.
