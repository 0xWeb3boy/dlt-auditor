# Validation Card

## Metadata

- ID: `rippled-2024-02-02-rippled-core-logic-828bb64eb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`

## What Confirmed The Issue

- Evidence 1: Commit body states NFTokenAcceptOffer could succeed when the recipient lacked sufficient reserves for a new NFTokenPage.
- Evidence 2: Commit body states the corrected behavior is failure with tecINSUFFICIENT_RESERVE.

## What Could Have Invalidated It

- Compensating control 1: Provided snippets do not show the actual OwnerCount or reserve-check logic.
- Compensating control 2: No supplied evidence demonstrates theft, unauthorized transfer, or direct fund loss.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-accounting, economic-distortion
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: Provided snippets do not show the actual OwnerCount or reserve-check logic.
- Caution 2: No supplied evidence demonstrates theft, unauthorized transfer, or direct fund loss.
