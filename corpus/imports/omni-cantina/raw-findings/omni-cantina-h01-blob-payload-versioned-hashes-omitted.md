# Raw Finding Summary

Source: Omni Cantina `H-1`
Title: Blob transactions can halt the chain
Severity: `high`

## Normalized Summary

The report shows Omni passing an empty versionedHashes slice to NewPayloadV3. Blob transactions make geth expect non-empty hashes matching the blob transactions, so ProcessProposal rejects the payload and repeats.

## Reusable Failure Shape

Engine API V3 returns payload plus blob side data, but consensus serializes only the payload and validators replay it with an empty versioned-hash argument.

## Missing Property

`fork-specific-payload-side-argument-equivalence`: Every fork-specific execution payload imported by validators must carry, reject, or reconstruct the Engine API side arguments required for that fork.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `H-1`
