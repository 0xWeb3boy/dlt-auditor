# Validation Card

## Metadata

- ID: `optimism-2025-05-12-optimism-p2p-networking-7db6c1da87`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-state-machine-hardening`

## What Confirmed The Issue

- find_starting_forkchoice now detects inconsistent forkchoice tuples before traversal begins.
- The patch treats unsafe < safe/finalized as a corrupted execution-layer forkchoice state and normalizes all heads to the unsafe head.
- A dedicated recovery path was added for 'finality still at genesis' startup state instead of trusting the prior tuple.
- Derivation gating changed from raw block-number comparison to explicit has_changed() tracking, tightening when the pipeline may advance.

## What Could Have Invalidated It

- No proof that a remote or adversarial party can force the bad forkchoice states.
- No reproducer, test, or incident report showing exploitable consensus failure.
- No evidence of invalid block acceptance, privilege gain, fund loss, or data exposure.
- The snippets do not show the full surrounding logic, so downstream safety impact is inferred rather than demonstrated.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that a remote or adversarial party can force the bad forkchoice states.
- No reproducer, test, or incident report showing exploitable consensus failure.
- No evidence of invalid block acceptance, privilege gain, fund loss, or data exposure.
