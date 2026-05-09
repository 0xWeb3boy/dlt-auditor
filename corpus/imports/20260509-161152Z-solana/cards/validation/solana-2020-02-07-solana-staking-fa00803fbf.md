# Validation Card

## Metadata

- ID: `solana-2020-02-07-solana-staking-fa00803fbf`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `gossip-freshness-validation`

## What Confirmed The Issue

- Pull-response CrdsValue entries are externally supplied gossip input before insertion into local CRDS state.
- The patch adds pre-insertion timeout checks for expired and far-future wallclock values.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
