# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-06-06-sei-chain-transaction-processing-beccf236c`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass-hardening`

## Code Shape Summary

- The patch changes gov precompile vote and deposit handling to construct Cosmos SDK governance messages, call ValidateBasic, and dispatch through the gov MsgServer instead of calling keeper methods directly.

## Search Motifs

- Motif 1: precompile calls keeper directly instead of MsgServer
- Motif 2: ValidateBasic absent before governance mutation
- Motif 3: native and EVM paths duplicate validation logic

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Construct canonical SDK messages, run basic validation, and dispatch through the standard MsgServer.

## False Match Warnings

- The direct keeper method performs exactly the same validation.
- The precompile method is read-only or disabled.
