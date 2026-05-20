# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-positive-result-33242`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`

## Code Shape Summary

- The sign branch for IFP multiply and divide used only self.non_negative, making all results non-negative.

## Search Motifs

- IFP64 multiply non_negative
- IFP divide divisor sign missing
- always returns positive
- signed fixed point sign matrix

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Compare both operands when setting non_negative and add sign-matrix tests for IFP64, IFP128, and IFP256.

## False Match Warnings

- No issue if the affected library version is not used.
- No issue if negative values are rejected before all IFP multiply/divide calls.
