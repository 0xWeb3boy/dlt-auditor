# Code-Shape Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-8f939340a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-confirmation-depth`

## Code Shape Summary

- Short description of what the buggy code looked like: The pre-change design did not have a separate verifier-specific confirmation-delay path in the shown head-forwarding logic; derivation received the newest observed L1 head directly. The patch introduces an optional delayed-fetch path, but the provided evidence does not prove that the earlier behavior was a vulnerability rather than a missing hardening control.

## Search Motifs

- Motif 1: latest observed head is forwarded directly despite a configured confirmation-delay policy
- Motif 2: startup or wake-up logic trusts requested state before confirming the engine or source state is initialized
- Motif 3: policy values are logged or stored but not enforced consistently on downstream reads

## Typical Asymmetry

- What was checked in one path but missing in another: The code distinguished between observed head state and safer delayed or initialized state in one place, but another path still consumed the fresher or unchecked state directly.

## Patch Pattern

- What the fix changed structurally: Add a separate confirmation-aware input path for verifier derivation while preserving immediate real-head visibility for other consumers, and instrument the new delayed-fetch behavior with metrics and tests.

## False Match Warnings

- What looks similar but is often not a bug: This supports consensus-safety hardening, not a proven vulnerability remediation.
