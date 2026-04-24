# Code-Shape Card

## Metadata

- ID: `sui-2022-05-03-sui-transaction-processing-601889c18e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The evidence supports a conservative security-hardening finding for Sui authority follower batch streaming. The strongest grounded change is resource-control hardening: authority-side request bounds were added, and SafeClient now tracks streamed item count with an inline comment identifying the guard as protection against.

## Search Motifs

- resource-accounting enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Add layered resource bounds to a streaming protocol: validate request ranges at the authority side, centralize stream range computation, and add a client-side consumption limit for overlong responses.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
