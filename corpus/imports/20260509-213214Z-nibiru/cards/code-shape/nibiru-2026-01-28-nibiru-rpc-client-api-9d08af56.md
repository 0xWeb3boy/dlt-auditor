# Code-Shape Card

## Metadata

- ID: `nibiru-2026-01-28-nibiru-rpc-client-api-9d08af56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vulnerable-dependency`

## Code Shape Summary

- A security advisory remediation upgraded the CometBFT dependency to a patched version across module manifests and checksums.

## Search Motifs

- commit references CSA or security advisory
- go.mod/go.sum-only upgrade for consensus dependency
- same dependency pinned in root and internal SDK modules
- patched version mentioned in commit body

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Pin the patched upstream version consistently in every relevant module and refresh lock/checksum files so builds cannot resolve the vulnerable baseline.

## False Match Warnings

- Dependency churn alone is not security without advisory or version evidence
- Do not invent the upstream root cause if the advisory details are absent
- Ensure all build modules, not just tests, resolve to the patched version
