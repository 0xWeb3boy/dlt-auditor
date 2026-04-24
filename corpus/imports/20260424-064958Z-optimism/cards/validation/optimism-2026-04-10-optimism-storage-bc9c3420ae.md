# Validation Card

## Metadata

- ID: `optimism-2026-04-10-optimism-storage-bc9c3420ae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-validation`

## What Confirmed The Issue

- Missing proof-window state now returns NoBlocksFound instead of Ok(None).
- Block-order validation now compares against proof_window.latest.hash rather than a B256::ZERO fallback.
- Reorg replacement now rejects bases outside the stored [earliest, latest] proof window.
- Regression coverage changed from permissive no-op success to explicit error on uninitialized pruning.

## What Could Have Invalidated It

- No call-path evidence shows untrusted external input can trigger these storage mutations.
- No proof that the old behavior led to exploitable corruption, forgery, or privilege gain.
- No evidence of consensus divergence, proof bypass, or real-world exploitability.
- Commit message and patch do not describe a disclosed security issue or incident.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No call-path evidence shows untrusted external input can trigger these storage mutations.
- No proof that the old behavior led to exploitable corruption, forgery, or privilege gain.
- No evidence of consensus divergence, proof bypass, or real-world exploitability.
