# Code-Shape Card

## Metadata

- ID: `go-ethereum-2020-12-08-go-ethereum-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`

## Code Shape Summary

- The prior helper API defaulted to Homestead signing and did not let these entry points express EIP-155 chain-domain separation. The supported root cause is legacy/default signing behavior without chainID selection, not missing authorization.

## Search Motifs

- Motif 1: rpc method missing exact checks for replay protection
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Add explicit chainID-aware transaction signer construction and update affected entry points that need chain-specific signing to use it, while retaining the legacy Homestead helper as deprecated compatibility API

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Add explicit chainID-aware transaction signer construction and update affected entry points that need chain-specific signing to use it, while retaining the legacy Homestead helper as deprecated compatibility API.

## False Match Warnings

- Classify as replay-protection hardening, not access control.
- Do not claim a proven security fix for an exploited vulnerability.
