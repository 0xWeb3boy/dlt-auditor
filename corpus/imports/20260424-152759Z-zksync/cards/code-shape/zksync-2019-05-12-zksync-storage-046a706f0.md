# Code-Shape Card

## Metadata

- ID: `zksync-2019-05-12-zksync-storage-046a706f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-missing-storage-record`

## Code Shape Summary

- A read API handler used a request-derived block id to fetch a required COMMIT operation and called a panic path when the record was absent. The reusable shape is an infallible unwrap/expect at an external API to storage boundary, fixed by returning a typed not-found response before unwrapping.

## Search Motifs

- expect or unwrap after DB lookup keyed by route parameter
- load_*_by_id result assumed present in HTTP/RPC handler
- comment or patch replacing panic with not found/error response

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Convert the storage lookup to an optional/result value, branch on absence, return a structured API error, and only unwrap or dereference after the presence check.

## False Match Warnings

- Missing records that are impossible due to an earlier authenticated workflow are less compelling.
- Panics in offline tools, tests, or one-shot migration code are not equivalent to request-path DoS.
- Adjacent response-format or timestamp changes should not be counted as the security fix.
