# Validation Card

## Metadata

- ID: `optimism-2024-06-26-optimism-transaction-processing-d1ea098c1f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-proof-state-hash`

## What Confirmed The Issue

- cannon/cmd/run.go changes the proof path from hashing witness state before stepFn(true) to using a post-step hash.
- The commit subject explicitly says Fix post-state hash in proof, matching the code change.
- witness.go, provider.go, and prestate.go consolidate callers onto a canonical EncodeWitness() return value for both witness bytes and hash.
- The touched subsystem is Cannon/fault-proof trace generation, where commitment correctness is security-sensitive.

## What Could Have Invalidated It

- No proof that an invalid proof or claim was actually accepted before the patch.
- No attacker-controlled input or exploit path is shown in the supplied diff.
- No evidence of funds loss, consensus impact, or verifier bypass is provided.
- The snippets do not show whether the bug was reachable outside internal tooling or only caused correctness failures.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an invalid proof or claim was actually accepted before the patch.
- No attacker-controlled input or exploit path is shown in the supplied diff.
- No evidence of funds loss, consensus impact, or verifier bypass is provided.
