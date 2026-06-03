# Root-Cause Card

Record: `omni-cantina-h04-malformed-consensus-pubkey-admission`
Project: `omni-network`
Source finding: `Omni Cantina H-4`
Bug family: `input_validation_and_invariant_enforcement`

## Core Failure

Validation is syntactic at ingress and semantic only at a later liveness-critical sink.

## Why It Matters

A delayed parser failure after value acceptance can become consensus failure instead of a rejected registration.

## Reusable Heuristic

Distinguish length/type checks from semantic parsing for public keys, proofs, commitments, and encoded cross-runtime values.

## Patch Direction

Validate compressed secp256k1 public keys at createValidator or deliverCreateValidator before accepting/storing the validator creation.
