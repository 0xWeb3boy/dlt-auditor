# Validation Card

## Metadata

- ID: `solana-2020-02-14-solana-staking-535ee281e8`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `peer-gossip-freshness-validation`

## What Confirmed The Issue

- Pull responses previously inserted each CRDS value without the shown explicit stale or future wallclock filter at that call site.
- After the patch, CRDS values from pull responses are checked against msg_timeout before insertion.

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
