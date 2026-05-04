# Validation Card

## Metadata

- ID: `stacks-core-2019-08-29-stacks-core-cryptography-6b6cbd3f36`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-constructor-validation`

## What Confirmed The Issue

- Evidence 1: In `src/vm/types/mod.rs`, the patch replaces `if expected_type.size()? > MAX_VALUE_SIZE {` with `// Constructors for TypeSignature ensure that the size of the Value cannot`.
- Evidence 2: In `src/vm/types/mod.rs`, the patch replaces `let type_sig = TypeSignature::construct_parent_list_type(&list_data)?;` with `// Constructors for TypeSignature ensure that the size of the Value cannot`.

## What Could Have Invalidated It

- Compensating control 1: The constructor may be used only with trusted constants.
- Compensating control 2: The changed path may improve diagnostics without changing acceptance behavior.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The constructor may be used only with trusted constants.
- Caution 2: The changed path may improve diagnostics without changing acceptance behavior.
