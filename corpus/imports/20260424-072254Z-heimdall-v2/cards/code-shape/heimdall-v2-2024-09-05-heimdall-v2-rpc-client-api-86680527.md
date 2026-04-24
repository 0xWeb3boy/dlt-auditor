# Code-Shape Card

## Metadata

- ID: `heimdall-v2-2024-09-05-heimdall-v2-rpc-client-api-86680527`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-height-validation`

## Code Shape Summary

- A tally function decoded vote extensions without receiving the current consensus height. The patch threads `currentHeight` through the call chain and rejects vote-extension payloads whose embedded height is not the expected prior height.

## Search Motifs

- Motif 1: `aggregateVotes`, `tallyVotes`, or attestation aggregation accepts payloads but lacks height or round parameters.
- Motif 2: explicit validation-gap comments near height, hash, domain, or round checks.
- Motif 3: patch adds `currentHeight`, `req.Height`, or `height-1` comparison before counting.

## Typical Asymmetry

- Payloads carry self-declared context, but only the surrounding consensus request supplies authoritative context.

## Patch Pattern

- Propagate authoritative context from the ABCI request into lower-level aggregation and reject mismatched embedded context before validator vote counting.

## False Match Warnings

- This is not a finding if another mandatory verifier already binds the payload to height before aggregation or if the embedded height is never used for decisions.
