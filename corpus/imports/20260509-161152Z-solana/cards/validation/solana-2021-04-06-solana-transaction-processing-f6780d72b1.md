# Validation Card

## Metadata

- ID: `solana-2021-04-06-solana-transaction-processing-f6780d72b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `faucet-rate-limit-scope`

## What Confirmed The Issue

- Commit subject and body state faucet cap and slice arguments were changed to apply to single IPs.
- TCP faucet handler now resolves stream.peer_addr() before processing and fails with ERROR_RESPONSE when the peer address cannot be obtained.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: availability_or_resource_exhaustion
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
