# Validation Card

## Metadata

- ID: `snarkos-2025-03-11-snarkos-core-logic-27575e79c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integer-overflow-in-input-validation`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Use overflow-safe arithmetic and express the full structural locator invariant without wrapping additions.
- Root-cause evidence from the finding: Validation arithmetic was performed on a height value that the fixed code documents as untrusted, while the old code assumed `u32` block heights would not approach the overflow boundary. 1. `check_block_locators` validates recent block locators and checkpoint locators, producing `last_recent_height` and `last_checkpoint_height`. 2. The function then checks that the last checkpoint height is correctly positioned relative to the last recent height and `CHECKPOINT_INTERVAL`. 3. Before the patch, th

## What Could Have Invalidated It

- Deserializer rejects heights above protocol maximum.
- Earlier validation enforces checkpoint height bounds.

## Severity Guidance

- Expected impact band: `validation-hardening`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls malformed locator passes/fails incorrectly; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If input is already capped far below overflow, impact is low
- Arithmetic in comments or tests is not a sink
- Wrapping used intentionally for protocol-defined modular arithmetic is different
