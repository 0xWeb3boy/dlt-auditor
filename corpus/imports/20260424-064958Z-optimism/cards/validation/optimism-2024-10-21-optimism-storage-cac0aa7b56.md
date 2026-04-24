# Validation Card

## Metadata

- ID: `optimism-2024-10-21-optimism-storage-cac0aa7b56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-frontier-validation`

## What Confirmed The Issue

- CrossUnsafeUpdate now rejects a candidate when bl.ParentHash != crossUnsafe.Hash before promoting the cross-unsafe frontier.
- The worker now returns early when no cross-unsafe starting point exists, replacing a prior unfinished/unfinished work marker path.
- IsCrossUnsafe(...) adds explicit state-query logic around the tracked cross-unsafe frontier with defined error cases.
- StartingBlock() exposes an explicit initial sealed block for state anchoring, consistent with safer initialization of supervisor state.

## What Could Have Invalidated It

- The provided snippets do not prove the pre-patch system lacked equivalent continuity validation elsewhere.
- No attacker-controlled trigger or exploit path is shown in the supplied evidence.
- No concrete downstream security impact is demonstrated, such as consensus bypass, forged cross-chain execution, fund loss, or privilege gain.
- The commit message and mixed file changes suggest general correctness/plumbing work in addition to the hardening change.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- The provided snippets do not prove the pre-patch system lacked equivalent continuity validation elsewhere.
- No attacker-controlled trigger or exploit path is shown in the supplied evidence.
- No concrete downstream security impact is demonstrated, such as consensus bypass, forged cross-chain execution, fund loss, or privilege gain.
