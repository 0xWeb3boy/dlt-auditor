# Code-Shape Card

## Metadata

- ID: `agave-2025-10-15-agave-p2p-networking-589d58b07f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `connection-rate-limit-hardening`

## Code Shape Summary

- A QUIC ingress path checks whether requests are allowed but does not consistently consume token-bucket capacity at the point where connection work proceeds.

## Search Motifs

- is_allowed used instead of consume_tokens in admission path
- global request limiter checked after expensive connection setup
- per IP register connection does not consume token
- token bucket ordering around handshake

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Replace non-consuming allowance checks with explicit token consumption and add early global request-budget gates before continuing connection handling.

## False Match Warnings

- The allowance check is only advisory and a later mandatory consume gate precedes all expensive work.
- Lower transport layers already enforce the same per-peer budget.
- The path is not remotely reachable.
