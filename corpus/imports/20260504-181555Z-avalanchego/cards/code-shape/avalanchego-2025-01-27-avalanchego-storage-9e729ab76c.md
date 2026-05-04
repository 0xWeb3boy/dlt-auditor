# Code-Shape Card

## Metadata

- ID: `avalanchego-2025-01-27-avalanchego-storage-9e729ab76c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-resource-control`

## Code Shape Summary

- A maxQueryLimit check was added for caller-supplied reward percentiles before fee-history processing. The reusable shape is an RPC endpoint that bounds array cardinality independently of per-element validation.

## Search Motifs

- len(userArray) > maxQueryLimit near RPC entry
- rewardPercentiles or similar arrays processed in fee history/oracle code
- errInvalidPercentile or query limit errors added before loops

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Reject oversized caller-controlled arrays at RPC entry using an existing query limit before per-element validation or computation.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Public endpoints behind strict gateway limits may reduce severity
- Small fixed-size arrays or server-generated arrays are not matches
- Do not conflate copy-initialization refactors with RPC resource controls
