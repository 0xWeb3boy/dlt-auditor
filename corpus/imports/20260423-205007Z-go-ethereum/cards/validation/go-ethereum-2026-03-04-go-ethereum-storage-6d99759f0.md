# Validation Card

## Metadata

- ID: `go-ethereum-2026-03-04-go-ethereum-storage-6d99759f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-persistent-state-side-effect`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says it prevents state flushing in RPC.
- Evidence 2: ExecutionWitness is an RPC/debug API path that calls ProcessBlock to generate a stateless witness.

## What Could Have Invalidated It

- Compensating control 1: Treat as hardening against unintended persistent side effects from RPC/debug execution, not as a proven vulnerability fix.
- Compensating control 2: Do not claim cryptographic, replay-protection, validator, or consensus-rule fixes from the supplied evidence.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Treat as hardening against unintended persistent side effects from RPC/debug execution, not as a proven vulnerability fix.
- Caution 2: Do not claim cryptographic, replay-protection, validator, or consensus-rule fixes from the supplied evidence.
