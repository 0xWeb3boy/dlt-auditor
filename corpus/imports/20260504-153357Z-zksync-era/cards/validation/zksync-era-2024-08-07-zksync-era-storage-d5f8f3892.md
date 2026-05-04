# Validation Card

## Metadata

- ID: `zksync-era-2024-08-07-zksync-era-storage-d5f8f3892`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `strict-consensus-genesis-parsing`

## What Confirmed The Issue

- Evidence 1: Stored and fetched consensus genesis paths now deserialize with unknown fields denied.
- Evidence 2: Comments state the node should not operate when unsupported consensus protocol fields are present, especially before hashing genesis.

## What Could Have Invalidated It

- Compensating control 1: A separate protocol-version gate rejects unsupported genesis before decoding.
- Compensating control 2: Unknown fields are part of an explicitly canonical, forward-compatible encoding and are included in the hash.

## Severity Guidance

- Expected impact band: consensus-integrity-hardening
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Do not infer remote genesis injection without evidence that an attacker controls the bytes.
- Caution 2: Treat as hardening unless a fork, validator corruption, or denial-of-service path is demonstrated.
