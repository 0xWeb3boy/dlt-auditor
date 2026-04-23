# Code-Shape Card

## Metadata

- ID: `nitro-2023-10-13-nitro-storage-f88557d06`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-metering`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a likely security fix for undercharging in the native/JIT Stylus activation path. The patch adds explicit gas-in/gas-out handling across the ArbOS-to-Rust activation boundary and burns the consumed amount afterward.

## Search Motifs

- Motif 1: cross-language execution APIs take gas in but do not return gas out
- Motif 2: native or JIT activation burns gas only after a patch threads remaining gas back
- Motif 3: resource consumption spans a subsystem boundary and the caller assumes the callee accounted for it

## Typical Asymmetry

- What was checked in one path but missing in another: The execution path consumed real resources across a subsystem boundary, but the accounting layer treated the call as opaque and never charged the delta at the authoritative sink.

## Patch Pattern

- What the fix changed structurally: Thread a mutable gas budget through the cross-language activation call, return the remaining gas to the caller, and charge the consumed delta at the protocol burner layer.

## False Match Warnings

- What looks similar but is often not a bug: If a later accounting layer already charges the same work exactly once, similar cross-boundary refactors may be benign.
