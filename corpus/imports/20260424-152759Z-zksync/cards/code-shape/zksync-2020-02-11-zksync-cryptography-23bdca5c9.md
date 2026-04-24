# Code-Shape Card

## Metadata

- ID: `zksync-2020-02-11-zksync-cryptography-23bdca5c9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-binding-in-circuit`

## Code Shape Summary

- The patch carries the ChangePubKey nonce through witness data, operation arguments, and pubdata, then constrains it equal to the current account nonce. The reusable shape is a replay/order field present in transaction semantics but absent or unconstrained in proof/public-data plumbing.

## Search Motifs

- nonce added to witness struct and operation arguments
- pub_nonce constrained equal to cur.account.nonce
- pubdata serialization updated to include transaction nonce

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Thread nonce through witness and public-data structures, then add an equality constraint against committed account state.

## False Match Warnings

- If account nonce was already checked in a parent circuit or mempool gate, this may be consistency hardening only.
- Do not infer direct fund loss without a demonstrated accepted replay.
- Pure serialization refactors without a constraint are weaker signals.
