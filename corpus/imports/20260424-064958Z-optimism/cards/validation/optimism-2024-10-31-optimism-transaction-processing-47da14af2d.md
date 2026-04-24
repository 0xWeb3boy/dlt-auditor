# Validation Card

## Metadata

- ID: `optimism-2024-10-31-optimism-transaction-processing-47da14af2d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-payload-handling`

## What Confirmed The Issue

- payload_process.go adds Holocene-specific handling for ExecutionInvalid / ExecutionInvalidBlockHash and requests deposits-only attributes instead of following the ordinary invalid path.
- deriver.go wires a new DepositsOnlyPayloadAttributesRequestEvent into the derivation pipeline, showing an explicit recovery path for invalid payload attributes.
- attributes_queue.go now clears lastAttribs during reset, reducing the risk of stale derived state being reused after invalid payload handling.
- types.go adds IsDepositsOnly(), indicating the fallback path intentionally constrains payload contents to deposit transactions only.

## What Could Have Invalidated It

- No advisory, bug report, or commit text states that a security vulnerability existed before the patch.
- The diff does not show attacker control, exploit steps, or a demonstrated chain split / remote DoS scenario.
- The provided test evidence does not include assertions proving a concrete pre-patch security failure.
- Nothing in the shown patch supports the original resource-exhaustion classification.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No advisory, bug report, or commit text states that a security vulnerability existed before the patch.
- The diff does not show attacker control, exploit steps, or a demonstrated chain split / remote DoS scenario.
- The provided test evidence does not include assertions proving a concrete pre-patch security failure.
