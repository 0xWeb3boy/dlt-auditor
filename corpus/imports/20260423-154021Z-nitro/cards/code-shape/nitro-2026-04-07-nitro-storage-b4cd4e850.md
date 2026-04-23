# Code-Shape Card

## Metadata

- ID: `nitro-2026-04-07-nitro-storage-b4cd4e850`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-guard`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch is best supported as runtime hardening for native stack-overflow handling, not as a demonstrated security fix. The shown changes bound stack-growth retry behavior and update tests around that path, but the provided evidence does not establish an exploitable vulnerability or a protocol-level security violation.

## Search Motifs

- Motif 1: trap handlers double stack or memory allocations without one-time guards
- Motif 2: recovery retries are not restricted to the execution context they were designed for
- Motif 3: tests are added later to prove only one bounded retry occurs after stack overflow

## Typical Asymmetry

- What was checked in one path but missing in another: The recovery path was designed to save execution after a fault, but it lacked the same bounded-resource assumptions that the steady-state execution path expected.

## Patch Pattern

- What the fix changed structurally: Add an explicit one-time guard to a recovery path, cap resource growth, restrict the behavior by execution context, and add tests that exercise the bounded retry flow.

## False Match Warnings

- What looks similar but is often not a bug: If the trap is unreachable under production limits, similar code may not be security-relevant.
