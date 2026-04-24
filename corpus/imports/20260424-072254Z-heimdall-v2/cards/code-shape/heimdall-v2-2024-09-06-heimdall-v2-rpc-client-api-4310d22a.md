# Code-Shape Card

## Metadata

- ID: `heimdall-v2-2024-09-06-heimdall-v2-rpc-client-api-4310d22a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-extension-validation`

## Code Shape Summary

- Proposal handlers performed inline unmarshalling and duplicate-response checks over vote extensions. The patch replaces those narrow checks with a shared `ValidateVoteExtensions` call that receives consensus context and validator state, then rejects proposal processing failures.

## Search Motifs

- Motif 1: `PrepareProposal` or `ProcessProposal` loops over vote extensions and only unmarshals payloads.
- Motif 2: comments or helper names mention vote-extension signatures, validator set, or two-thirds majority.
- Motif 3: patch replaces duplicated inline loops with `Validate*`, `Verify*`, or quorum-check helper.

## Typical Asymmetry

- A payload can be syntactically valid while not being signed by the right validators or not representing quorum for the relevant round.

## Patch Pattern

- Centralize vote-extension validation at proposal boundaries, pass height/proposer/round/validator state into the helper, and reject before accepting proposal data.

## False Match Warnings

- A pure refactor to a helper is not enough; look for added context, signature, validator-set, or quorum validation and for rejection behavior at proposal acceptance.
