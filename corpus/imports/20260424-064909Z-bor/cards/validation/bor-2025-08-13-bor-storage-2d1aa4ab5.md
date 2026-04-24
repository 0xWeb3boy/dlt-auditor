# Validation Card

## Metadata

- ID: `bor-2025-08-13-bor-storage-2d1aa4ab5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-header-validation`

## What Confirmed The Issue

- core/blockchain.go adds bc.hc.ValidateHeaderChain(headers) before pre-cutoff header insertion.
- The affected path handles canonical headers before the configured chain cutoff, a consensus- and state-sensitive operation.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof that untrusted or remote input could reach this path in an exploitable way.
- No demonstration of a concrete consensus split, privilege boundary crossing, or denial-of-service outcome.
