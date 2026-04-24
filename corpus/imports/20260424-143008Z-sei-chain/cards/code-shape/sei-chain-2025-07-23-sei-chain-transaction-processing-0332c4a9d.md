# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-07-23-sei-chain-transaction-processing-0332c4a9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `entrypoint-scope-enforcement`

## Code Shape Summary

- The supported finding is security hardening in the Sei EVM Solo precompile. The strongest evidence is that the generic Claim entrypoint previously discarded the concrete validated claim message and then transferred all balances from the sender, while the patch keeps the message and rejects MsgClaimSpecific.

## Search Motifs

- Motif 1: validated message returned but discarded
- Motif 2: generic Claim path accepts MsgClaimSpecific
- Motif 3: precompile lacks caller-runtime guard before transfer

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Preserve and inspect the concrete validated message, reject out-of-scope message types and disallowed caller runtimes before transfer.

## False Match Warnings

- The validator guarantees only the expected concrete message reaches the generic path.
- The transfer amount is zero or independently scoped downstream.
