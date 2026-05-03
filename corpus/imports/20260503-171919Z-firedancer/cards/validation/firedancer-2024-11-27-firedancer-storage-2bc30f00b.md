# Validation Card

## Metadata

- ID: `firedancer-2024-11-27-firedancer-storage-2bc30f00b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `crypto-precompile-input-validation-hardening`

## What Confirmed The Issue

- Evidence 1: The runtime secp256r1 precompile previously returned success for data_sz == 2 and data[0] == 0 inside an undersized-data branch; the patch now reports an instruction data size error.
- Evidence 2: The patched code is on a signature verification precompile path exposed to transaction instruction data.

## What Could Have Invalidated It

- Compensating control 1: No end-to-end transaction or exploit proof shows that invalid signatures were accepted before the patch.
- Compensating control 2: No demonstrated consensus divergence, funds-at-risk, privilege bypass, or authentication bypass is provided.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No end-to-end transaction or exploit proof shows that invalid signatures were accepted before the patch.
- Caution 2: No demonstrated consensus divergence, funds-at-risk, privilege bypass, or authentication bypass is provided.
