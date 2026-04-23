# Code-Shape Card

## Metadata

- ID: `go-ethereum-2026-03-04-go-ethereum-storage-6d99759f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-persistent-state-side-effect`

## Code Shape Summary

- ProcessBlock mixed normal import side effects with debug/RPC execution use cases. The old boolean controls distinguished head updates and witness generation, but did not clearly express a read-only mode, allowing a non-head-updating execution path to still persist block/state data.

## Search Motifs

- Motif 1: rpc method missing exact checks for rpc persistent state side effect
- Motif 2: security-sensitive path reaches persistent state writes or canonical-head side effects behind an RPC/debug path before rejecting malformed or unauthorized input
- Motif 3: Replace ambiguous boolean execution controls with explicit configuration flags and gate persistent write operations behind a dedicated WriteState option

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Replace ambiguous boolean execution controls with explicit configuration flags and gate persistent write operations behind a dedicated WriteState option.

## False Match Warnings

- Treat as hardening against unintended persistent side effects from RPC/debug execution, not as a proven vulnerability fix.
- Do not claim cryptographic, replay-protection, validator, or consensus-rule fixes from the supplied evidence.
