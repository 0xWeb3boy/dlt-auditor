# Validation Card

## Metadata

- ID: `zksync-era-2024-12-04-zksync-era-transaction-processing-1c0098489`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-configuration-validation`

## What Confirmed The Issue

- Evidence 1: Genesis validation now errors when the on-chain FFLONK verification key hash differs from configured `fflonk_snark_wrapper_vk_hash`.
- Evidence 2: FFLONK hash reads now select the intended overloaded ABI function explicitly.

## What Could Have Invalidated It

- Compensating control 1: The ABI has no overload or the prior call helper already selected by full signature.
- Compensating control 2: The value is not used to gate genesis, proof verification, or consensus-relevant configuration.

## Severity Guidance

- Expected impact band: configuration-integrity-hardening
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Do not claim invalid proof acceptance without proof-system reachability evidence.
- Caution 2: Diagnostic-only contract reads are weaker than genesis acceptance checks.
