# Code-Shape Card

## Metadata

- ID: `agave-2025-12-27-agave-cryptography-346847efe6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-state-validation-timing`

## Code Shape Summary

- Nonce authority and account state are validated early in bank transaction-age handling, then reused later even though the nonce account is mutable before SVM processing.

## Search Motifs

- durable nonce authority checked before execution and not reloaded
- NonceInfo constructed during transaction age check
- closed reopened spoofed nonce account comment
- mutable account state validated too early

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Defer nonce execution-state construction to SVM processing and reload/revalidate the current nonce account and authority immediately before processing.

## False Match Warnings

- Strict account locks make nonce state immutable between check and execution.
- The execution boundary reloads and revalidates nonce state before any effect.
- The early check is only a cache hint and not trusted for acceptance.
