# Code-Shape Card

## Metadata

- ID: `scroll-2023-08-18-scroll-transaction-processing-767a2cbf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-transition`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence shows a focused state-machine fix in the coordinator proof receiver: after a chunk or batch is already verified, the code now skips later chunk/batch-level status updates for all incoming statuses instead of only `ProvingTaskFailed`. That supports a post-verification integrity/correctness hardening claim. The provided diff does not establish an attacker-driven vulnerability, cryptographic bypass, or consensus-impacting exploit.

## Search Motifs

- Motif 1: success state only guards one failure status instead of all later updates
- Motif 2: proof receiver mutates persistent task state after verified status is already set
- Motif 3: terminal lifecycle state is not enforced as immutable in updateProofStatus-style paths

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Make the verified status terminal and short-circuit all later state transitions that would otherwise revisit chunk or batch status after success.

## False Match Warnings

- Warning 1: If later status messages are append-only telemetry and cannot alter the canonical task status, a similar pattern may be benign.
- Warning 2: If the state transition is wrapped in a stronger idempotency guard or compare-and-swap on terminal status, the downgrade risk is lower.
- Warning 3: The evidence supports lifecycle integrity hardening, not a demonstrated proof-verification bypass.
