# Validation Card

## Metadata

- ID: `nitro-2023-10-13-nitro-storage-f88557d06`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-metering`

## What Confirmed The Issue

- Evidence 1: The evidence supports a likely security fix for undercharging in the native/JIT Stylus activation path.
- Evidence 2: Thread a mutable gas budget through the cross-language activation call, return the remaining gas to the caller, and charge the consumed delta at the protocol burner layer.

## What Could Have Invalidated It

- Compensating control 1: If a later accounting layer already charges the same work exactly once, similar cross-boundary refactors may be benign.
- Compensating control 2: If the feature is gated behind non-production settings, classify similar cases as hardening.

## Severity Guidance

- Expected impact band: `resource_accounting`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: If a later accounting layer already charges the same work exactly once, similar cross-boundary refactors may be benign.
- Caution 2: Do not claim economic exploitation without evidence that the undercharge reaches final gas or fee accounting.
