# Code-Shape Card

## Metadata

- ID: `heimdall-v2-2024-06-24-heimdall-v2-rpc-client-api-316e7e65`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-id-reuse-guard`

## Code Shape Summary

- A create/join handler checks whether an identity has already been used by calling a getter and interpreting its error. The patch adds a direct `Has`/existence helper and rejects when the key is present.

## Search Motifs

- Motif 1: `Get*From*ID` used inside duplicate-registration or reuse guard.
- Motif 2: guard checks `err != nil` or `err == nil` from a getter to decide uniqueness.
- Motif 3: patch adds `Exists`, `Has`, `Do*Exist`, or direct store presence check.

## Typical Asymmetry

- Read APIs return errors for many reasons, while uniqueness checks need a precise key-present/key-absent answer.

## Patch Pattern

- Add a key-presence helper on the canonical mapping and use it before any registration state mutation; keep value retrieval separate.

## False Match Warnings

- Not every getter-to-exists refactor is security-relevant. Prioritize identity, signer, validator, account, operator, or authorization namespaces reachable from state-changing messages.
