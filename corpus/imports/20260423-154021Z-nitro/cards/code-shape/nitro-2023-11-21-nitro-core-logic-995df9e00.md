# Code-Shape Card

## Metadata

- ID: `nitro-2023-11-21-nitro-core-logic-995df9e00`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `error-handling-policy`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch changes the prover VM's error-guard behavior from implicitly recovering whenever a guard frame exists to recovering only when an explicit `enabled` policy bit is set. That is a real control-flow hardening change, but the provided evidence does not establish a concrete vulnerability, attacker trigger, or protocol impact.

## Search Motifs

- Motif 1: VMs infer recovery permission from internal stack presence rather than an explicit enabled bit
- Motif 2: guard or trap frames persist after the policy that created them should have expired
- Motif 3: patches add explicit enable flags to error-guard stacks or recovery metadata

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Add explicit policy state for recovery behavior and enforce it at the decision point instead of inferring permission from leftover internal state.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
