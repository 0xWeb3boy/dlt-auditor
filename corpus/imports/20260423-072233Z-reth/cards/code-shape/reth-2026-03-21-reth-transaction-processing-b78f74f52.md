# Code-Shape Card

## Metadata

- ID: `reth-2026-03-21-reth-transaction-processing-b78f74f52`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`

## Code Shape Summary

- Broad validator exceptions for special payload forms allowed hash or state-root checks to be skipped. The patch removes zero-hash sentinel behavior, always compares the executed state root to the header, and narrows env-switch handling to receipt-derived fields only.

## Search Motifs

- zero hash sentinel skips validation
- env_switches or segmented block bypasses post execution checks
- special case path skips state root or block hash comparison

## Typical Asymmetry

- The code has one path that performs the expected validation, accounting, or quality update while a nearby special-case, cache-hit, early-return, or alternate response path omits it.

## Patch Pattern

- Replace broad special-case bypasses with a dedicated narrow validator that preserves core identity and state checks while skipping only explicitly non-comparable fields.

## False Match Warnings

- Pure benchmark or replay-only compatibility code is not enough without a production validation path.
- Skipping receipt-derived checks can be legitimate when cumulative receipt fields are structurally non-comparable.
- Do not claim exploitability unless untrusted payloads can reach the special-case branch.
