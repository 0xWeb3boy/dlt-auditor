# Root-Cause Card

Record: `omni-cantina-m03-signature-malleability-raw-duplicate`
Project: `omni-network`
Source finding: `Omni Cantina M-3`
Bug family: `signature_binding_and_signer_scope`

## Core Failure

The verifier and storage layer disagree about identity: one admits by semantic signer recovery, the other rejects by raw byte equality.

## Why It Matters

Malleable encodings can break liveness even when they do not forge a signer or change the signed message.

## Reusable Heuristic

Whenever a signature verifier accepts a semantic signer/message, inspect downstream replay, duplicate, and slashing code for raw-byte comparisons.

## Patch Direction

Canonicalize or reject malleable signatures before storage, and treat same signer/root duplicates as idempotent once the signature has verified.
