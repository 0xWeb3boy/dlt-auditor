# Root-Cause Card

## Metadata

- ID: `solana-2020-02-14-solana-staking-535ee281e8`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `peer-gossip-freshness-validation`
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

The grounded root cause is incomplete explicit freshness validation in the shown CRDS gossip pull-response ingestion path. Claims about a proven security exploit, consensus failure, arbitrary wallclock control, or direct fund impact are not supported by the provided evidence.

## Impact Pattern

- Primary impact: gossip-state-integrity, stale-peer-data-rejection
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds explicit stale and future wallclock filtering for CRDS gossip pull responses before insertion into CRDS, threads stake/epoch-derived timeout data into packet handling, and changes a push timeout check to use checked_add. This is plausibly security relevant because gossip data is peer supplied, but the provided evidence does not establish a concrete vulnerability, exploit path, consensus impact, or direct safety failure.
