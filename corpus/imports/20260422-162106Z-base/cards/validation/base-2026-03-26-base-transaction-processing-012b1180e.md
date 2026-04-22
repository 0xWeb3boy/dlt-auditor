# Validation Card

## Metadata

- ID: `base-2026-03-26-base-transaction-processing-012b1180e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-claim-validation`

## What Confirmed The Issue

- Evidence 1: The commit body explicitly describes a malicious-attacker scenario: anchoring a trace-extension claim at the wrong height while reusing the agreed output root.
- Evidence 2: Pre-patch `prologue.rs` returned `TraceExtension` based on output-root equality alone, without first validating the claimed L2 block number against the safe head.

## What Could Have Invalidated It

- Compensating control 1: Validated as a security fix only for the proof-client claim-validation change in `crates/proof/client/src/prologue.rs`.
- Compensating control 2: Do not overclaim confidentiality, code execution, or full consensus compromise from the provided patch alone.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Validated as a security fix only for the proof-client claim-validation change in `crates/proof/client/src/prologue.rs`.
- Caution 2: Do not overclaim confidentiality, code execution, or full consensus compromise from the provided patch alone.
