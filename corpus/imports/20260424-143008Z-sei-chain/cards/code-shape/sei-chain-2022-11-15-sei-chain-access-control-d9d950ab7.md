# Code-Shape Card

## Metadata

- ID: `sei-chain-2022-11-15-sei-chain-access-control-d9d950ab7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The patch adds a direct authorization gate to RegisterContract. The code now fetches wasm contract metadata for msg.Contract.ContractAddr and rejects the request with sdkerrors.ErrUnauthorized when contractInfo.Creator does not match msg.Creator. This supports a grounded missing-authorization finding for the DEX contract registration path.

## Search Motifs

- Motif 1: Msg creator compared only to request fields
- Motif 2: contract registration lacks wasm creator lookup
- Motif 3: state mutation uses contract address before owner check

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Fetch canonical ownership metadata from the owning subsystem and reject mismatched callers before registration state changes.

## False Match Warnings

- A prior ante or router layer already proves the sender is the contract creator.
- The registration has no privileged effect or is purely informational.
