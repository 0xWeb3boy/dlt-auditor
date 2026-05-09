# Root-Cause Card

## Metadata

- ID: `solana-2020-02-07-solana-staking-fa00803fbf`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `gossip-freshness-validation`
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

The supported root cause is incomplete freshness validation in the CRDS pull-response insertion path, plus direct timestamp addition that could overflow in related timeout checks. The evidence does not support broader claims about consensus compromise, privilege bypass, theft, or serialized state representation bugs.

## Impact Pattern

- Primary impact: network-state-integrity, state-consistency
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds freshness validation for CrdsValue entries received through gossip pull responses before inserting them into CRDS. It also threads stake/epoch-aware timeout data into packet handling and makes related push-message timeout arithmetic overflow-aware. This is plausibly security relevant because the data is peer-supplied gossip input, but the provided evidence does not prove a vulnerability impact beyond stale or future-timestamped values rea...
