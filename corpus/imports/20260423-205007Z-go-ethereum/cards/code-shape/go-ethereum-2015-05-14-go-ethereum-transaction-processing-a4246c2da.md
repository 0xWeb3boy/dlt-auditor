# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-05-14-go-ethereum-transaction-processing-a4246c2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unknown-parent-sync-hardening`

## Code Shape Summary

- The old downloader API conflated two different synchronization states: no queued head was ready, and a queued head could not connect to a known parent. That made an invalid or suspicious queued-head condition look like ordinary lack of work.

## Search Motifs

- Motif 1: rpc method missing exact checks for unknown parent sync hardening
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Split benign readiness checks from invariant failures

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Split benign readiness checks from invariant failures. Return an explicit error for invalid synchronization state and require the caller to abort instead of silently treating it as no work.

## False Match Warnings

- Classify as block downloader synchronization hardening, not transaction processing.
- Do not claim confirmed remote DoS from the supplied patch alone.
