# Validation Card

## Metadata

- ID: `zksync-2019-05-12-zksync-storage-046a706f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-missing-storage-record`

## What Confirmed The Issue

- A route/path value is parsed and used directly in the COMMIT storage lookup.
- The pre-fix lookup reached an expect/panic when storage returned no row.
- The patch adds an explicit None branch returning a normal API error.

## What Could Have Invalidated It

- A prior guard proves the requested id always has a COMMIT operation.
- The panic is fully contained and cannot affect availability or user-visible service behavior.

## Severity Guidance

- Expected impact band: `availability`
- Expected severity band: `medium_or_low`
- Rationale: A request can plausibly trigger a panic in a public read path, but the evidence does not prove full node shutdown, fund loss, or consensus impact.

## False-Positive Cautions

- Missing records that are impossible due to an earlier authenticated workflow are less compelling.
- Panics in offline tools, tests, or one-shot migration code are not equivalent to request-path DoS.
