# Code-Shape Card

## Metadata

- ID: `snarkos-2025-03-11-snarkos-core-logic-27575e79c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integer-overflow-in-input-validation`

## Code Shape Summary

- Block locator validation performs arithmetic on untrusted height values while assuming u32 heights cannot approach overflow boundaries.

## Search Motifs

- height + interval in validation condition
- comment says value is untrusted but unchecked arithmetic follows
- checked_add or saturating comparison added to locator validation

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Use overflow-safe arithmetic and express the full structural locator invariant without wrapping additions.

## False Match Warnings

- If input is already capped far below overflow, impact is low
- Arithmetic in comments or tests is not a sink
- Wrapping used intentionally for protocol-defined modular arithmetic is different
